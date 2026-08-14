import type { PersistedMatchRankResponse } from '@mosaic/contracts';
import { useRouter } from 'expo-router';
import { useEffect, useState } from 'react';
import { StyleSheet, Text, View } from 'react-native';

import { AppScreen } from '@/components/AppScreen';
import { PrimaryButton } from '@/components/PrimaryButton';
import { rankMatches } from '@/lib/engine';
import { useAuth } from '@/providers/AuthProvider';
import { theme } from '@/theme';

const internalAlphaCandidates = [
  '10000000-0000-4000-8000-000000000001',
  '10000000-0000-4000-8000-000000000002',
  '10000000-0000-4000-8000-000000000003',
  '10000000-0000-4000-8000-000000000004',
  '10000000-0000-4000-8000-000000000005',
] as const;

const rankingRequest = {
  candidate_ids: [...internalAlphaCandidates],
  limit: internalAlphaCandidates.length,
};

export default function MatchesScreen() {
  const router = useRouter();
  const { session, loading } = useAuth();
  const accessToken = session?.access_token;
  const [ranking, setRanking] = useState<PersistedMatchRankResponse | null>(null);
  const [busy, setBusy] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (loading) return;
    if (!accessToken) {
      router.replace('/auth');
      return;
    }

    let active = true;
    void rankMatches(accessToken, rankingRequest)
      .then((result) => {
        if (!active) return;
        setRanking(result);
        setError(null);
      })
      .catch((rankingError: unknown) => {
        if (!active) return;
        setError(rankingError instanceof Error ? rankingError.message : 'Unable to load ranking.');
      })
      .finally(() => {
        if (active) setBusy(false);
      });

    return () => {
      active = false;
    };
  }, [accessToken, loading, router]);

  async function retryRanking() {
    if (!accessToken) return;
    setBusy(true);
    setError(null);
    try {
      setRanking(await rankMatches(accessToken, rankingRequest));
    } catch (rankingError: unknown) {
      setError(rankingError instanceof Error ? rankingError.message : 'Unable to load ranking.');
    } finally {
      setBusy(false);
    }
  }

  return (
    <AppScreen scroll>
      <View style={styles.header}>
        <Text style={styles.eyebrow}>PHASE 8 INTERNAL ALPHA</Text>
        <Text style={styles.title}>Versioned mock candidate ranking.</Text>
        <Text style={styles.body}>
          This list proves the authenticated ranking and persistence path. Scores are deterministic
          infrastructure fixtures and are not compatibility, attraction, or relationship predictions.
        </Text>
      </View>

      {ranking ? (
        <>
          <View style={styles.provenance}>
            <Text style={styles.provenanceLabel}>PERSISTED RANKING RUN</Text>
            <Text style={styles.provenanceValue}>{ranking.run_id}</Text>
            <Text style={styles.provenanceMeta}>Model {ranking.model_version}</Text>
            <Text style={styles.provenanceMeta}>
              Request {ranking.request_fingerprint.slice(0, 16)}…
            </Text>
          </View>

          <View style={styles.list}>
            {ranking.ranked_candidates.map((candidate) => (
              <View key={candidate.candidate_id} style={styles.card}>
                <Text style={styles.rank}>#{candidate.rank}</Text>
                <View style={styles.cardBody}>
                  <Text style={styles.candidate}>Mock candidate {candidate.candidate_id.slice(-4)}</Text>
                  <Text style={styles.score}>Deterministic score {candidate.rank_score.toFixed(4)}</Text>
                </View>
              </View>
            ))}
          </View>
        </>
      ) : null}

      {error ? <Text style={styles.error}>{error}</Text> : null}

      <View style={styles.actions}>
        {error ? (
          <PrimaryButton disabled={busy} onPress={() => void retryRanking()}>
            Retry ranking
          </PrimaryButton>
        ) : null}
        <PrimaryButton disabled={busy} onPress={() => router.replace('/home')}>
          Return home
        </PrimaryButton>
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
  provenance: {
    borderWidth: 1,
    borderColor: theme.colors.border,
    borderRadius: theme.radius.card,
    backgroundColor: theme.colors.surface,
    padding: theme.spacing.lg,
    gap: theme.spacing.xs,
    marginBottom: theme.spacing.lg,
  },
  provenanceLabel: {
    color: theme.colors.muted,
    fontSize: 11,
    fontWeight: '700',
    letterSpacing: 1.1,
  },
  provenanceValue: {
    color: theme.colors.text,
    fontSize: 13,
    fontWeight: '700',
  },
  provenanceMeta: {
    color: theme.colors.muted,
    fontSize: 13,
  },
  list: {
    gap: theme.spacing.sm,
    marginBottom: theme.spacing.xl,
  },
  card: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: theme.spacing.md,
    borderWidth: 1,
    borderColor: theme.colors.border,
    borderRadius: theme.radius.card,
    backgroundColor: theme.colors.surface,
    padding: theme.spacing.lg,
  },
  rank: {
    color: theme.colors.text,
    fontSize: 26,
    fontWeight: '800',
  },
  cardBody: {
    flex: 1,
    gap: theme.spacing.xs,
  },
  candidate: {
    color: theme.colors.text,
    fontSize: 17,
    fontWeight: '700',
  },
  score: {
    color: theme.colors.muted,
    fontSize: 13,
  },
  error: {
    color: theme.colors.error,
    fontSize: 14,
    lineHeight: 20,
    marginBottom: theme.spacing.md,
  },
  actions: {
    gap: theme.spacing.sm,
  },
});
