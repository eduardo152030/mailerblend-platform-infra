"""Local proposal only: classify a failed attempt; never starts or mutates a job."""
from dataclasses import dataclass


@dataclass(frozen=True)
class Recovery:
    action: str
    message: str
    allow_talker_automatically: bool = False
    preserve_original: bool = True


def classify(*, terminal, processes_stopped, checkpoint, same_identity, eos):
    """checkpoint is a verified result: absent/partial/invalid/valid, not path.exists()."""
    if not terminal or not processes_stopped:
        return Recovery('wait_or_cancel', 'El intento no está completamente detenido; no iniciar otro motor.')
    if checkpoint == 'valid' and same_identity and eos:
        return Recovery('offer_decoder_only', 'Códigos íntegros con EOS: puede reanudarse solo la conversión a WAV por acción explícita.')
    if checkpoint == 'valid':
        return Recovery('review_identity_or_EOS', 'No reanudar: el modelo/referencia/texto o EOS no coincide con el checkpoint.')
    if checkpoint in ('partial', 'invalid'):
        return Recovery('preserve_and_review', 'Checkpoint incompleto o inválido; conservarlo. No continuar desde Decoder ni repetir Talker automáticamente.')
    if checkpoint == 'absent':
        return Recovery('offer_new_attempt_explicitly', 'No se guardaron códigos de esta narración. Reintentar requiere una nueva inferencia, con otro intento y tras resolver la causa original.')
    raise ValueError('Unknown checkpoint verification result')
