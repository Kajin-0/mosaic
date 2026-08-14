import type {
  MeasurementNextResponse,
  MeasurementResponseRequest,
} from '@mosaic/contracts';
import * as Crypto from 'expo-crypto';
import { useRouter } from 'expo-router';
import { useEffect, useState } from 'react';
import { StyleSheet, Text, View } from 'react-native';

import { AppScreen } from '@/components/AppScreen';
import { PrimaryButton } from '@/components/PrimaryButton';
import { getNextMeasurementItem, submitMeasurementResponse } from '@/lib/engine';
import { useAuth } from '@/providers/AuthProvider';
import { theme } from '@/theme';

export default function OnboardingMeasurementScreen() {
  const router = useRouter();
  const { session, profile, loading, setLifecycleState } = useAuth();
  const accessToken = session?.access_token;
  const [measurement, setMeasurement] = useState<MeasurementNextResponse | null>(null);
  const [pending, setPending] = useState<MeasurementResponseRequest | null>(null);
  const [busy, setBusy] = useState(true);
  const [finishing, setFinishing] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function loadNext() {
    if (!accessToken) return;
    setBusy(true);
    setError(null);
    try {
      const next = await getNextMeasurementItem(accessToken);
      setMeasurement(next);
      setPending(null);
    } catch (loadError: unknown) {
      setError(loadError instanceof Error ? loadError.message : 'Unable to load measurement item.');
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
    if (profile?.lifecycle_state === 'active') {
      router.replace('/home');
      return;
    }

    let cancelled = false;
    getNextMeasurementItem(accessToken)
      .then((next) => {
        if (cancelled) return;
        setMeasurement(next);
        setPending(null);
        setError(null);
        setBusy(false);
      })
      .catch((loadError: unknown) => {
        if (cancelled) return;
        setError(loadError instanceof Error ? loadError.message : 'Unable to load measurement item.');
        setBusy(false);
      });

    return () => {
      cancelled = true;
    };
  }, [accessToken, loading, profile?.lifecycle_state, router]);

  async function sendResponse(request: MeasurementResponseRequest) {
    if (!accessToken) return;
    setBusy(true);
    setError(null);
    try {
      await submitMeasurementResponse(accessToken, request);
      await loadNext();
    } catch (submitError: unknown) {
      setError(submitError instanceof Error ? submitError.message : 'Unable to submit response.');
    } finally {
      setBusy(false);
    }
  }

  function choose(answer: MeasurementResponseRequest['answer']) {
    if (!measurement?.presentation_id) return;
    const request: MeasurementResponseRequest = {
      session_id: measurement.session_id,
      presentation_id: measurement.presentation_id,
      client_response_id: Crypto.randomUUID(),
      answer,
      client_timestamp: new Date().toISOString(),
    };
    setPending(request);
    void sendResponse(request);
  }

  async function finishOnboarding() {
    setFinishing(true);
    setError(null);
    try {
      await setLifecycleState('active');
      router.replace('/home');
    } catch (finishError: unknown) {
      setError(finishError instanceof Error ? finishError.message : 'Unable to update profile state.');
    } finally {
      setFinishing(false);
    }
  }

  if (measurement?.status === 'complete') {
    return (
      <AppScreen>
        <View style={styles.header}>
          <Text style={styles.eyebrow}>PHASE 5 MEASUREMENT</Text>
          <Text style={styles.title}>Measurement record complete.</Text>
          <Text style={styles.body}>
            Twenty versioned mock items and their raw responses are persisted. These items are infrastructure fixtures and do not yet represent a validated relationship assessment.
          </Text>
        </View>
        <View style={styles.progressBox}>
          <Text style={styles.progressValue}>
            {measurement.completed_item_count} / {measurement.target_item_count}
          </Text>
          <Text style={styles.progressLabel}>immutable raw responses stored</Text>
        </View>
        {error ? <Text style={styles.error}>{error}</Text> : null}
        <PrimaryButton disabled={finishing} onPress={() => void finishOnboarding()}>
          {finishing ? 'Saving…' : 'Finish onboarding'}
        </PrimaryButton>
      </AppScreen>
    );
  }

  const item = measurement?.item;

  return (
    <AppScreen scroll>
      <View style={styles.header}>
        <Text style={styles.eyebrow}>PHASE 5 MEASUREMENT</Text>
        <Text style={styles.title}>Build a versioned relationship profile.</Text>
        <Text style={styles.body}>
          The current 20-item instrument is a deterministic infrastructure test. Your progress is server-owned and resumes after interruption.
        </Text>
      </View>

      <View style={styles.progressBox}>
        <Text style={styles.progressValue}>
          {measurement ? measurement.completed_item_count : 0} / {measurement?.target_item_count ?? 20}
        </Text>
        <Text style={styles.progressLabel}>completed</Text>
      </View>

      {item ? (
        <View style={styles.itemCard}>
          <Text style={styles.itemKind}>{item.kind.replace('_', ' ').toUpperCase()}</Text>
          <Text style={styles.prompt}>{item.prompt}</Text>

          {item.kind === 'rating' ? (
            <View style={styles.ratingBlock}>
              <View style={styles.ratingLabels}>
                <Text style={styles.anchor}>{item.min_label}</Text>
                <Text style={styles.anchor}>{item.max_label}</Text>
              </View>
              <View style={styles.actions}>
                {[1, 2, 3, 4, 5].map((value) => (
                  <PrimaryButton
                    key={value}
                    disabled={busy}
                    onPress={() => choose({ kind: 'rating', value })}
                  >
                    {String(value)}
                  </PrimaryButton>
                ))}
              </View>
            </View>
          ) : null}

          {item.kind === 'hard_constraint' || item.kind === 'scenario' ? (
            <View style={styles.actions}>
              {item.options.map((option) => (
                <PrimaryButton
                  key={option.id}
                  disabled={busy}
                  onPress={() => choose({ kind: 'choice', option_id: option.id })}
                >
                  {option.label}
                </PrimaryButton>
              ))}
            </View>
          ) : null}

          {item.kind === 'forced_choice' ? (
            <View style={styles.actions}>
              <PrimaryButton
                disabled={busy}
                onPress={() => choose({ kind: 'choice', option_id: item.left.id })}
              >
                {item.left.label}
              </PrimaryButton>
              <PrimaryButton
                disabled={busy}
                onPress={() => choose({ kind: 'choice', option_id: item.right.id })}
              >
                {item.right.label}
              </PrimaryButton>
            </View>
          ) : null}
        </View>
      ) : null}

      {error ? <Text style={styles.error}>{error}</Text> : null}

      {pending && error ? (
        <PrimaryButton disabled={busy} onPress={() => void sendResponse(pending)}>
          Retry same submission
        </PrimaryButton>
      ) : null}
      {!measurement && !busy ? (
        <PrimaryButton onPress={() => void loadNext()}>Reload item</PrimaryButton>
      ) : null}
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
    fontSize: 32,
    lineHeight: 38,
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
  itemCard: {
    borderWidth: 1,
    borderColor: theme.colors.border,
    borderRadius: theme.radius.card,
    backgroundColor: theme.colors.surface,
    padding: theme.spacing.lg,
    marginBottom: theme.spacing.lg,
    gap: theme.spacing.md,
  },
  itemKind: {
    color: theme.colors.muted,
    fontSize: 11,
    fontWeight: '700',
    letterSpacing: 1.1,
  },
  prompt: {
    color: theme.colors.text,
    fontSize: 21,
    lineHeight: 29,
    fontWeight: '700',
  },
  actions: {
    gap: theme.spacing.sm,
  },
  ratingBlock: {
    gap: theme.spacing.md,
  },
  ratingLabels: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    gap: theme.spacing.md,
  },
  anchor: {
    flex: 1,
    color: theme.colors.muted,
    fontSize: 12,
    lineHeight: 17,
  },
  error: {
    color: theme.colors.error,
    fontSize: 14,
    lineHeight: 20,
    marginBottom: theme.spacing.md,
  },
});
