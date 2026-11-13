import { test } from 'node:test';
import assert from 'node:assert/strict';
import { isOptionAvailable } from '../../services/infra-voicebox/candidate-d083/ui/components/Generation/ct627Policy.ts';

test('unavailable Chatterbox is hidden even when a package is installed', () => {
  const opt = { engine: 'chatterbox', value: 'chatterbox' };
  assert.equal(isOptionAvailable(opt, {}), false);
  assert.equal(isOptionAvailable(opt, { chatterbox: { ready: false } }), false);
  assert.equal(isOptionAvailable(opt, { chatterbox: { ready: true } }), true);
});
test('Qwen UI permits only approved0.6B and rejects stale worker capabilities', () => {
  const caps = { qwen: { ready: true } };
  assert.equal(isOptionAvailable({engine: 'qwen', value: 'qwen:0.6B'}, caps), true);
  assert.equal(isOptionAvailable({engine: 'qwen', value: 'qwen:1.7B'}, caps), false);
  assert.equal(isOptionAvailable({engine: 'qwen', value: 'qwen:0.6B'}, {}), false);
});
test('resident-model managers cannot expose an unapproved engine', () => {
  assert.equal(isOptionAvailable({engine:'luxtts',value:'luxtts'}, {luxtts:{ready:true}}), false);
  assert.equal(isOptionAvailable({engine:'kokoro',value:'kokoro'}, {kokoro:{ready:true}}), true);
});

test('Qwen language chooser exposes exactly Spanish and English', async () => {
  const { getLanguageOptionsForEngine } = await import('../../services/infra-voicebox/candidate-d083/ui/lib/constants/languages.ts');
  assert.deepEqual(getLanguageOptionsForEngine('qwen').map(x => x.value).sort(), ['en','es']);
  assert.deepEqual(getLanguageOptionsForEngine('chatterbox').map(x => x.value).sort(), ['en','es']);
  assert.equal(isOptionAvailable({engine:'chatterbox',value:'chatterbox'}, {chatterbox:{ready:'false'}}), false);
});
