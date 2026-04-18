import test from 'node:test';
import assert from 'node:assert/strict';

import { buildAnalyzeMealRequest } from '../src/api/analyzeMeal.js';

test('buildAnalyzeMealRequest sends the original file as multipart form data', async () => {
  const largeBytes = new Uint8Array(16 * 1024);
  for (let index = 0; index < largeBytes.length; index += 1) {
    largeBytes[index] = index % 251;
  }

  const file = new File([largeBytes], 'meal-a.jpg', { type: 'image/jpeg' });
  const request = buildAnalyzeMealRequest({
    file,
    profile: {
      goal: 'maintain',
      diet: 'non-veg',
      conditions: ['low_sodium'],
      daily_calorie_target: 2000,
    },
    dailyIntake: {
      total_calories: 520,
      total_protein_g: 28,
      total_sodium_mg: 610,
    },
  });

  assert.equal(request.url, '/analyze');
  assert.equal(request.init.method, 'POST');
  assert.ok(request.init.body instanceof FormData);

  const formData = request.init.body;
  const uploadedFile = formData.get('file');
  assert.ok(uploadedFile instanceof File);
  assert.equal(uploadedFile.name, 'meal-a.jpg');
  assert.equal(uploadedFile.type, 'image/jpeg');
  assert.equal(uploadedFile.size, largeBytes.length);

  const uploadedBytes = new Uint8Array(await uploadedFile.arrayBuffer());
  assert.deepEqual(uploadedBytes, largeBytes);
  assert.equal(typeof formData.get('profile'), 'string');
  assert.equal(typeof formData.get('daily_intake'), 'string');

  const serialized = new Request('http://localhost/analyze', request.init);
  assert.match(serialized.headers.get('content-type'), /^multipart\/form-data; boundary=/);

  const payloadBytes = new Uint8Array(await serialized.arrayBuffer());
  assert.ok(payloadBytes.byteLength > uploadedFile.size);
  assert.ok(payloadBytes.byteLength > 8 * 1024);

  const payloadText = new TextDecoder().decode(payloadBytes);
  assert.match(payloadText, /name="file"; filename="meal-a\.jpg"/);
  assert.doesNotMatch(payloadText, /blob:/);
  assert.doesNotMatch(payloadText, /data:image\//);
});
