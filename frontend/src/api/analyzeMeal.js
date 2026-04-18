function resolveApiBaseUrl() {
  const configuredUrl = import.meta?.env?.VITE_API_URL?.trim();

  // Ignore placeholder values so local dev can fall back to the Vite proxy.
  if (configuredUrl && !configuredUrl.includes('<cloud-run-url>')) {
    return configuredUrl.replace(/\/$/, '');
  }

  return '';
}

export function buildAnalyzeMealRequest({
  file,
  profile = null,
  dailyIntake = {
    total_calories: 0,
    total_protein_g: 0,
    total_sodium_mg: 0,
  },
}) {
  if (!file) {
    throw new Error('An image file is required.');
  }

  const formData = new FormData();
  formData.append('file', file, file.name);

  if (profile) {
    formData.append('profile', JSON.stringify(profile));
  }

  formData.append('daily_intake', JSON.stringify(dailyIntake));

  const apiBaseUrl = resolveApiBaseUrl();

  return {
    url: `${apiBaseUrl}/analyze`,
    init: {
      method: 'POST',
      body: formData,
    },
  };
}

export async function checkBackendHealth() {
  try {
    const apiBaseUrl = resolveApiBaseUrl();
    const res = await fetch(`${apiBaseUrl}/health`);
    if (!res.ok) {
      return {
        status: "error",
        api_key_loaded: false,
        gemini_model: "error",
        gemini_message: "Backend health check failed.",
      };
    }
    return await res.json();
  } catch (err) {
    console.error("Health check failed", err);
    return {
      status: "error",
      api_key_loaded: false,
      gemini_model: "error",
      gemini_message: "Cannot reach backend.",
    };
  }
}

export async function analyzeMeal(params) {
  const request = buildAnalyzeMealRequest(params);
  const response = await fetch(request.url, request.init);

  if (!response.ok) {
    let message = 'Failed to analyze image. Please try again.';
    try {
      const errorBody = await response.json();
      if (typeof errorBody?.detail === 'string' && errorBody.detail.trim()) {
        if (errorBody.detail.includes('RESOURCE_EXHAUSTED') || errorBody.detail.toLowerCase().includes('quota')) {
          message = 'Gemini API is not working right now because the quota is exhausted. Please wait and try again.';
        } else {
          message = errorBody.detail;
        }
      }
    } catch (error) {
      console.error('Failed to parse backend error response', error);
    }

    throw new Error(message);
  }

  return response.json();
}
