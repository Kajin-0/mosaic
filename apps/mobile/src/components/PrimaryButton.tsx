import type { ReactNode } from 'react';
import { Pressable, StyleSheet, Text } from 'react-native';

import { theme } from '@/theme';

type PrimaryButtonProps = {
  children: ReactNode;
  onPress: () => void;
  testID?: string;
};

export function PrimaryButton({ children, onPress, testID }: PrimaryButtonProps) {
  return (
    <Pressable
      accessibilityRole="button"
      onPress={onPress}
      testID={testID}
      style={({ pressed }) => [styles.button, pressed && styles.pressed]}
    >
      <Text style={styles.label}>{children}</Text>
    </Pressable>
  );
}

const styles = StyleSheet.create({
  button: {
    minHeight: 54,
    alignItems: 'center',
    justifyContent: 'center',
    borderRadius: theme.radius.button,
    backgroundColor: theme.colors.accent,
    paddingHorizontal: theme.spacing.lg,
  },
  pressed: {
    opacity: 0.82,
  },
  label: {
    color: theme.colors.accentText,
    fontSize: 17,
    fontWeight: '700',
  },
});
