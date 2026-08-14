import type { CalibrationNextResponse, CalibrationResponseChoice, CalibrationResponseRequest } from '@mosaic/contracts';
import * as Crypto from 'expo-crypto';
import { useRouter } from 'expo-router';
import { useCallback, useEffect, useState } from 'react';
import { StyleSheet, Text, View } from 'react-native';

import { AppScreen } from '@/components/AppScreen';
import { PrimaryButton } from '@/components/PrimaryButton';
import { getNextCalibrationTrial, submitCalibrationResponse } from '@/lib/engine';
import { useAuth } from '@/providers/AuthProvider';
import { theme } from '@/theme';

const choiceLabels: Record<CalibrationResponseChoice, string> = {
  left: 'Left',
  right: 'Right',
  both: 'Both',
  neither: 'Neither',
};

export default function CalibrationScreen() {
  const router = useRouter();
  const { session, loading } = useAuth();
  const [trial, setTrial] = useState<CalibrationNextResponse | null>(null);
  const [pending, setPending] = useState<CalibrationResponseRequest | null>(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const loadNext = useCallback(async () => {
    if (!session?.access_token) return;
    setBusy(true);
    setError(null);
    try {
      const next = await getNextCalibrationTrial(session.access_token);
      setTrial(next);
      setPending(null);
    } catch (loadError: unknown) {
      setError(loadError instanceof Error ? loadError.message : 'Unable to load calibration trial.');
    } finally {
      setBusy(false);
    }
  }, [session?.access_token]);

  useEffect(() => {
    if (loading) return;
    if (!session) {
      router.replace('/auth');
      return;
    }
    void loadNext();
  }, [loadNext, loading, router, session]);

  async function sendResponse(request: CalibrationResponseRequest) {
    if (!session?.access_token) return;
    setBusy(true);
    setError(null);
    try {
      await submitCalibrationResponse(session.access_token, request);
      await loadNext();
    } catch (submitError: unknown) {
      setError(submitError instanceof Error ? submitError.message : 'Unable to submit response.');
    } finally {
      setBusy(false);
    }
  }

  function choose(response: CalibrationResponseChoice) {
    if (!trial?.experiment_id) return;
    const request: CalibrationResponseRequest = {
      session_id: trial.session_id,
      experiment_id: trial.experiment_id,
      client_response_id: Crypto.randomUUID(),
      response,
      client_timestamp: new Date().toISOString(),
    };
    setPending(request);
    void sendResponse(request);
  }

  if (trial?.status === 'complete') {
    return (
      <AppScreen>
        <View style={styles.header}>
          <Text style={styles.eyebrow}>PHASE 4 CALIBRATION</Text>
          <Text style={styles.title}>Ten persisted trials complete.</Text>
          <Text style={styles.body}>
            This is infrastructure validation only. The text pairs are deterministic mock stimuli and do not yet claim psychometric or matchmaking validity.
          </Text>
        </View>
        <View style={styles.progressBox}>
          <Text style={styles.progressValue}>
            {trial.completed_trial_count} / {trial.target_trial_count}
          </Text>
          <Text style={styles.progressLabel}>responses persisted</Text>
        </View>
        <PrimaryButton onPress={() => router.replace('/home')}>Return home</PrimaryButton>
      </AppScreen>
    );
  }

  return (
    <AppScreen scroll>
      <View style={styles.header}>
        <Text style={styles.eyebrow}>PHASE 4 CALIBRATION</Text>
        <Text style={styles.title}>Choose the option you prefer.</Text>
        <Text style={styles.body}>
          Deterministic text-only trials are being used to validate authentication, persistence, resume behavior, and idempotent writes.
        </Text>
      </View>

      <View style={styles.progressBox}>
        <Text style={styles.progressValue}>
          {trial ? trial.completed_trial_count : 0} / {trial?.target_trial_count ?? 10}
        </Text>
        <Text style={styles.progressLabel}>completed</Text>
      </View>

      {trial?.stimulus ? (
        <View style={styles.pair}>
          <View style={styles.optionCard}>
            <Text style={styles.optionLabel}>LEFT</Text>
            <Text style={styles.optionText}>{trial.stimulus.left.label}</Text>
          </View>
          <View style={styles.optionCard}>
            <Text style={styles.optionLabel}>RIGHT</Text>
            <Text style={styles.optionText}>{trial.stimulus.right.label}</Text>
          </View>
        </View>
      ) : null}

      {error ? <Text style={styles.error}>{error}</Text> : null}

      <View style={styles.actions}>
        {trial?.response_options.map((choice) => (
          <PrimaryButton key={choice} disabled={busy} onPress={() => choose(choice)}>
            {choiceLabels[choice]}
          </PrimaryButton>
        ))}
        {pending && error ? (
          <PrimaryButton disabled={busy} onPress={() => void sendResponse(pending)}>
            Retry same submission
          </PrimaryButton>
        ) : null}
        {!trial && !busy ? <PrimaryButton onPress={() => void loadNext()}>Reload trial</PrimaryButton> : null}
      </View>
    </AppScreen>
  );
}

const styles = StyleSheet.create({
  header: {
    gap: theme.spacing.md,
    marginBottom: theme.spacing.xl,
  },
  eyebrow: {
    color: theme.colors.muted,
    fontSize: 12,
    fontWeight: '700',
    letterSpacing: 1.3,
  },
  title: {
    color: theme.colors.text,
    fontSize: 34,
    lineHeight: 40,
    fontWeight: '800',
    letterSpacing: -0.7,
  },
  body: {
    color: theme.colors.muted,
    fontSize: 16,
    lineHeight: 24,
  },
  progressBox: {
    borderWidth: 1,
    borderColor: theme.colors.border,
    borderRadius: theme.radius.card,
    padding: theme.spacing.lg,
    marginBottom: theme.spacing.lg,
    backgroundColor: theme.colors.surface,
  },
  progressValue: {
    color: theme.colors.text,
    fontSize: 24,
    fontWeight: '800',
  },
  progressLabel: {
    color: theme.colors.muted,
    marginTop: theme.spacing.xs,
  },
  pair: {
    gap: theme.spacing.md,
    marginBottom: theme.spacing.lg,
  },
  optionCard: {
    borderWidth: 1,
    borderColor: theme.colors.border,
    borderRadius: theme.radius.card,
    padding: theme.spacing.lg,
    minHeight: 120,
    justifyContent: 'center',
    backgroundColor: theme.colors.surface,
  },
  optionLabel: {
    color: theme.colors.muted,
    fontSize: 11,
    fontWeight: '700',
    letterSpacing: 1.1,
    marginBottom: theme.spacing.sm,
  },
  optionText: {
    color: theme.colors.text,
    fontSize: 20,
    lineHeight: 28,
    fontWeight: '700',
  },
  actions: {
    gap: theme.spacing.sm,
  },
  error: {
    color: theme.colors.error,
    fontSize: 14,
    lineHeight: 20,
    marginBottom: theme.spacing.md,
  },
});
