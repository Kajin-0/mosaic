import type {
  CalibrationResponseChoice,
  SyntheticCalibrationNextResponse,
  SyntheticCalibrationResponseRequest,
} from '@mosaic/contracts';
import * as Crypto from 'expo-crypto';
import { useRouter } from 'expo-router';
import { useEffect, useState } from 'react';
import { Image, StyleSheet, Text, View } from 'react-native';

import { AppScreen } from '@/components/AppScreen';
import { PrimaryButton } from '@/components/PrimaryButton';
import {
  getNextSyntheticCalibrationPair,
  submitSyntheticCalibrationResponse,
} from '@/lib/engine';
import { useAuth } from '@/providers/AuthProvider';
import { theme } from '@/theme';

const choiceLabels: Record<CalibrationResponseChoice, string> = {
  left: 'Left',
  right: 'Right',
  both: 'Both',
  neither: 'Neither',
};

export default function SyntheticCalibrationScreen() {
  const router = useRouter();
  const { session, loading } = useAuth();
  const accessToken = session?.access_token;
  const [trial, setTrial] = useState<SyntheticCalibrationNextResponse | null>(null);
  const [pending, setPending] = useState<SyntheticCalibrationResponseRequest | null>(null);
  const [busy, setBusy] = useState(true);
  const [error, setError] = useState<string | null>(null);

  async function loadNext() {
    if (!accessToken) return;
    setBusy(true);
    setError(null);
    try {
      const next = await getNextSyntheticCalibrationPair(accessToken);
      setTrial(next);
      setPending(null);
    } catch (loadError: unknown) {
      setError(
        loadError instanceof Error ? loadError.message : 'Unable to load synthetic calibration.',
      );
    } finally {
      setBusy(false);
    }
  }

  useEffect(() => {
    if (loading) return;
    if (!accessToken) {
      router.replace('/auth');
      return;
    }

    let cancelled = false;
    getNextSyntheticCalibrationPair(accessToken)
      .then((next) => {
        if (cancelled) return;
        setTrial(next);
        setPending(null);
        setError(null);
        setBusy(false);
      })
      .catch((loadError: unknown) => {
        if (cancelled) return;
        setError(
          loadError instanceof Error
            ? loadError.message
            : 'Unable to load synthetic calibration.',
        );
        setBusy(false);
      });

    return () => {
      cancelled = true;
    };
  }, [accessToken, loading, router]);

  async function sendResponse(request: SyntheticCalibrationResponseRequest) {
    if (!accessToken) return;
    setBusy(true);
    setError(null);
    try {
      await submitSyntheticCalibrationResponse(accessToken, request);
      await loadNext();
    } catch (submitError: unknown) {
      setError(
        submitError instanceof Error ? submitError.message : 'Unable to submit response.',
      );
    } finally {
      setBusy(false);
    }
  }

  function choose(response: CalibrationResponseChoice) {
    if (!trial?.pair) return;
    const request: SyntheticCalibrationResponseRequest = {
      session_id: trial.session_id,
      pair_id: trial.pair.pair_id,
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
          <Text style={styles.eyebrow}>PHASE 6 SYNTHETIC CALIBRATION</Text>
          <Text style={styles.title}>Twenty synthetic comparisons complete.</Text>
          <Text style={styles.body}>
            Every displayed candidate, pair assignment, and response is persisted with replayable
            provenance. This validates the experiment infrastructure, not attraction inference.
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
        <Text style={styles.eyebrow}>PHASE 6 SYNTHETIC CALIBRATION</Text>
        <Text style={styles.title}>Which person would you rather meet?</Text>
        <Text style={styles.body}>
          These candidates are synthetic calibration artifacts used to learn preferences. They are
          not real members. The current images are deterministic mock stimuli for infrastructure
          validation only.
        </Text>
      </View>

      <View style={styles.progressBox}>
        <Text style={styles.progressValue}>
          {trial ? trial.completed_trial_count : 0} / {trial?.target_trial_count ?? 20}
        </Text>
        <Text style={styles.progressLabel}>
          completed · {trial?.cache_ready ? 'comparison cache ready' : 'preparing comparisons'}
        </Text>
      </View>

      {trial?.pair ? (
        <View style={styles.pair}>
          <View style={styles.candidateCard}>
            <Text style={styles.optionLabel}>LEFT</Text>
            <Image
              source={{ uri: trial.pair.left.asset_uri }}
              style={styles.candidateImage}
              resizeMode="contain"
              accessibilityLabel="Synthetic left calibration candidate"
            />
          </View>
          <View style={styles.candidateCard}>
            <Text style={styles.optionLabel}>RIGHT</Text>
            <Image
              source={{ uri: trial.pair.right.asset_uri }}
              style={styles.candidateImage}
              resizeMode="contain"
              accessibilityLabel="Synthetic right calibration candidate"
            />
          </View>
        </View>
      ) : null}

      {error ? <Text style={styles.error}>{error}</Text> : null}

      <View style={styles.actions}>
        {(trial?.response_options ?? []).map((choice) => (
          <PrimaryButton key={choice} disabled={busy} onPress={() => choose(choice)}>
            {choiceLabels[choice]}
          </PrimaryButton>
        ))}
        {pending && error ? (
          <PrimaryButton disabled={busy} onPress={() => void sendResponse(pending)}>
            Retry same submission
          </PrimaryButton>
        ) : null}
        {!trial && !busy ? (
          <PrimaryButton onPress={() => void loadNext()}>Reload comparison</PrimaryButton>
        ) : null}
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
    flexDirection: 'row',
    gap: theme.spacing.sm,
    marginBottom: theme.spacing.lg,
  },
  candidateCard: {
    flex: 1,
    borderWidth: 1,
    borderColor: theme.colors.border,
    borderRadius: theme.radius.card,
    padding: theme.spacing.sm,
    backgroundColor: theme.colors.surface,
  },
  optionLabel: {
    color: theme.colors.muted,
    fontSize: 11,
    fontWeight: '700',
    letterSpacing: 1.1,
    marginBottom: theme.spacing.sm,
  },
  candidateImage: {
    width: '100%',
    aspectRatio: 180 / 220,
    borderRadius: theme.radius.card,
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
