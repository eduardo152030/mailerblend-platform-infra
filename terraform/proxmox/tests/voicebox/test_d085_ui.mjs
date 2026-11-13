import test from 'node:test';
import assert from 'node:assert/strict';
import { CHATTERBOX_MAX_CHARS, isOptionAvailable, textLimit } from '../../services/infra-voicebox/candidate-d085/ui/components/Generation/ct627Policy.ts';
import { getLanguageOptionsForEngine } from '../../services/infra-voicebox/candidate-d085/ui/lib/constants/languages.ts';
test('backend unavailable hides Chatterbox',()=>assert.equal(isOptionAvailable({engine:'chatterbox',value:'chatterbox'},{chatterbox:{ready:false}}),false));
test('prepared Chatterbox is independently selectable',()=>assert.equal(isOptionAvailable({engine:'chatterbox',value:'chatterbox'},{chatterbox:{ready:true}}),true));
test('both input budgets are1200; Qwen is preserved',()=>{assert.equal(textLimit('qwen'),1200);assert.equal(CHATTERBOX_MAX_CHARS,1200);assert.equal(textLimit('chatterbox'),1200);});
test('both cloning engines expose only es/en',()=>{for(const e of ['qwen','chatterbox'])assert.deepEqual(getLanguageOptionsForEngine(e).map(x=>x.value).sort(),['en','es']);});
import { prioritizeGenerationEffects } from '../../services/infra-voicebox/candidate-d085/ui/lib/constants/generationEffects.ts';
test('requested effects are offered first without removing custom presets or mutating input',()=>{
 const original=[{name:'Custom'},{name:'Deep Voice'},{name:'Radio'},{name:'Echo Chamber'},{name:'Robotic'}];
 assert.deepEqual(prioritizeGenerationEffects(original).map(x=>x.name),['Robotic','Radio','Echo Chamber','Deep Voice','Custom']);
 assert.equal(original[0].name,'Custom');
});
