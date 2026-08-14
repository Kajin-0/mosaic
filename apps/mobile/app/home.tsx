import { StyleSheet, Text, View } from 'react-native';

import { AppScreen } from '@/components/AppScreen';
import { theme } from '@/theme';

const modules = [
  ['Profile', 'Phase 2', 'Identity and persisted user state'],
  ['Calibration', 'Phase 4+', 'Adaptive measurement and synthetic trials'],
  ['Matches', 'Later', 'Directional attraction and dyadic ranking'],
] as const;

export default function HomePlaceholderScreen() {
  return (
    <AppScreen scroll>
      <View style={styles.header}>
        <Text style={styles.eyebrow}>PROTOTYPE HOME</Text>
        <Text style={styles.title}>Mobile shell online.</Text>
        <Text style={styles.body}>
          Phase 1 stops here deliberately. Product modules remain inert until their infrastructure
          boundaries are implemented and tested.
        </Text>
      </View>

      <View style={styles.moduleList}>
        {modules.map(([name, phase, description]) => (
          <View key={name} style={styles.card}>
            <View style={styles.cardTopline}>
              <Text style={styles.cardTitle}>{name}</Text>
              <Text style={styles.phase}>{phase}</Text>
            </View>
            <Text style={styles.cardBody}>{description}</Text>
          </View>
        ))}
      </View>

      <View style={styles.statusBox}>
        <Text style={styles.statusLabel}>PHASE 1 STATUS</Text>
        <Text style={styles.statusValue}>Navigation boundary established</Text>
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
    fontSize: 36,
    lineHeight: 42,
    fontWeight: '800',
    letterSpacing: -0.8,
  },
  body: {
    color: theme.colors.muted,
    fontSize: 16,
    lineHeight: 24,
  },
  moduleList: {
    gap: theme.spacing.sm,
  },
  card: {
    borderWidth: 1,
    borderColor: theme.colors.border,
    borderRadius: theme.radius.card,
    backgroundColor: theme.colors.surface,
    padding: theme.spacing.lg,
    gap: theme.spacing.sm,
  },
  cardTopline: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    gap: theme.spacing.md,
  },
  cardTitle: {
    color: theme.colors.text,
    fontSize: 20,
    fontWeight: '700',
  },
  phase: {
    color: theme.colors.muted,
    fontSize: 12,
    fontWeight: '700',
  },
  cardBody: {
    color: theme.colors.muted,
    fontSize: 15,
    lineHeight: 22,
  },
  statusBox: {
    marginTop: theme.spacing.xl,
    borderTopWidth: 1,
    borderTopColor: theme.colors.border,
    paddingTop: theme.spacing.lg,
    gap: theme.spacing.xs,
  },
  statusLabel: {
    color: theme.colors.muted,
    fontSize: 11,
    fontWeight: '700',
    letterSpacing: 1.1,
  },
  statusValue: {
    color: theme.colors.text,
    fontSize: 16,
    fontWeight: '600',
  },
});
