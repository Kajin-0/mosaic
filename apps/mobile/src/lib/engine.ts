import type {
  CalibrationNextRequest,
  CalibrationNextResponse,
  CalibrationResponseReceipt,
  CalibrationResponseRequest,
  MeasurementNextRequest,
  MeasurementNextResponse,
  MeasurementResponseReceipt,
  MeasurementResponseRequest,
  MeasurementScoreRequest,
  MeasurementScoreResponse,
} from '@mosaic/contracts';

const engineUrl = process.env.EXPO_PUBLIC_MOSAIC_ENGINE_URL?.replace(/\/$/, '');

export class EngineApiError extends Error {
  constructor(
    message: string,
    readonly status: number,
  ) {
    super(message);
  }
}

async function engineRequest<TResponse>(
  path: string,
  accessToken: string,
  body: unknown,
): Promise<TResponse> {
  if (!engineUrl) {
    throw new EngineApiError('EXPO_PUBLIC_MOSAIC_ENGINE_URL is not configured.', 0);
  }

  const response = await fetch(`${engineUrl}${path}`, {
    method: 'POST',
    headers: {
      Authorization: `Bearer ${accessToken}`,
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(body),
  });

  const text = await response.text();
  let payload: unknown = null;
  if (text) {
    try {
      payload = JSON.parse(text);
    } catch {
      payload = text;
    }
  }

  if (!response.ok) {
    const detail =
      typeof payload === 'object' && payload && 'detail' in payload
        ? String((payload as { detail: unknown }).detail)
        : `Mosaic engine request failed with HTTP ${response.status}.`;
    throw new EngineApiError(detail, response.status);
  }

  return payload as TResponse;
}

export function getNextCalibrationTrial(accessToken: string): Promise<CalibrationNextResponse> {
  const body: CalibrationNextRequest = {};
  return engineRequest<CalibrationNextResponse>('/v1/calibration/next', accessToken, body);
}

export function submitCalibrationResponse(
  accessToken: string,
  body: CalibrationResponseRequest,
): Promise<CalibrationResponseReceipt> {
  return engineRequest<CalibrationResponseReceipt>('/v1/calibration/response', accessToken, body);
}

export function getNextMeasurementItem(accessToken: string): Promise<MeasurementNextResponse> {
  const body: MeasurementNextRequest = {};
  return engineRequest<MeasurementNextResponse>('/v1/measurement/next', accessToken, body);
}

export function submitMeasurementResponse(
  accessToken: string,
  body: MeasurementResponseRequest,
): Promise<MeasurementResponseReceipt> {
  return engineRequest<MeasurementResponseReceipt>('/v1/measurement/response', accessToken, body);
}

export function scoreMeasurementSession(
  accessToken: string,
  body: MeasurementScoreRequest,
): Promise<MeasurementScoreResponse> {
  return engineRequest<MeasurementScoreResponse>('/v1/measurement/score', accessToken, body);
}
