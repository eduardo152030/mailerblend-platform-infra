#!/usr/bin/perl
use strict;
use warnings;
use File::Temp qw(tempdir);
use JSON::PP qw(decode_json);
use MIME::Base64 qw(encode_base64);
use PVE::Notify;

my $endpoint = 'telegram-native';
my $matcher = 'default-matcher';
my $old_target = 'mail-to-root';

sub b64 { return encode_base64($_[0], ''); }

sub configure {
    my ($config, $token, $chat) = @_;
    my ($current) = grep { $_->{name} eq $matcher } @{ $config->get_matchers() };
    die "Unexpected Proxmox notification matcher\n" if !$current || $current->{disable};
    my @old = @{ $current->{target} };
    return 0 if @old == 1 && $old[0] eq $endpoint;
    die "Unexpected Proxmox notification target\n" if @old != 1 || $old[0] ne $old_target;
    die "Webhook name already in use\n"
        if grep { $_->{name} eq $endpoint } @{ $config->get_webhook_endpoints() };

    $config->add_webhook_endpoint({
        name => $endpoint,
        method => 'post',
        url => 'https://api.telegram.org/bot{{ secrets.token }}/sendMessage',
        header => ['name=Content-Type,value=' . b64('application/json')],
        secret => ['name=token,value=' . b64($token), 'name=chat,value=' . b64($chat)],
        body => b64('{"chat_id":"{{ secrets.chat }}","text":"Proxmox: {{ escape title }}\nSeveridad: {{ escape severity }}"}'),
        comment => 'Avisos operativos de PVE a Telegram',
    });
    return 1;
}

sub switch_matcher {
    my ($config) = @_;
    $config->update_matcher(
        $matcher, [$endpoint],
        undef, undef, undef, undef, undef, undef, undef, undef, undef,
    );
}

sub backup {
    my ($config) = @_;
    my $dir = tempdir('before-pve-telegram.XXXXXXXX', DIR => '/root', CLEANUP => 0);
    my ($public, $private) = $config->write_config();
    for my $entry (['notifications.cfg', $public], ['private.cfg', $private]) {
        open my $file, '>', "$dir/$entry->[0]" or die "Could not open backup\n";
        print {$file} $entry->[1] // '';
        close $file or die "Could not commit backup\n";
    }
    return $dir;
}

if (@ARGV == 1 && $ARGV[0] eq '--self-test') {
    my $config = Proxmox::RS::Notify->parse_config('', '');
    configure($config, 'synthetic', '-1') or die "Fixture not changed\n";
    switch_matcher($config);
    my ($updated) = grep { $_->{name} eq $matcher } @{ $config->get_matchers() };
    die "Fixture routing mismatch\n" unless join(',', @{ $updated->{target} }) eq $endpoint;
    print "PASS: native webhook schema, matcher replacement and isolated fixture\n";
    exit 0;
}
die "Expected --apply and private JSON on stdin\n" unless @ARGV == 1 && $ARGV[0] eq '--apply';
umask 0077;
my $input = decode_json(do { local $/; <STDIN> });
my ($token, $chat) = @{$input}{qw(token chat)};
die "Invalid Telegram input\n" if !defined($token) || !defined($chat)
    || $token !~ /\A[0-9]+:[A-Za-z0-9_-]+\z/ || $chat !~ /\A-?[0-9]+\z/;

my $success = eval {
    PVE::Notify::lock_config(sub {
        my $original = PVE::Notify::read_config();
        my ($public, $private) = $original->write_config();
        my $candidate = Proxmox::RS::Notify->parse_config($public, $private);
        if (!configure($candidate, $token, $chat)) {
            print "Sin cambios\n";
            return;
        }
        my $dir = backup($original);
        print "Respaldo privado: $dir\n";
        $candidate->test_target($endpoint);
        switch_matcher($candidate);
        eval { PVE::Notify::write_config($candidate); 1 } or do {
            PVE::Notify::write_config($original);
            die "Write failed and previous routing restored\n";
        };
        print "Prueba nativa aceptada. Matcher actualizado a Telegram.\n";
    }, 15);
    1;
};
die "Proxmox Telegram transaction failed. Review the private backup and current route.\n" unless $success;
