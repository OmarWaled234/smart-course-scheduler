import { ActivityIndicator, Pressable, StyleSheet, Text, ViewStyle } from "react-native";

type PrimaryButtonProps = {
  title: string;
  onPress: () => void;
  disabled?: boolean;
  loading?: boolean;
  variant?: "primary" | "secondary" | "danger";
  style?: ViewStyle;
};

export function PrimaryButton({
  title,
  onPress,
  disabled,
  loading,
  variant = "primary",
  style
}: PrimaryButtonProps) {
  return (
    <Pressable
      accessibilityRole="button"
      disabled={disabled || loading}
      onPress={onPress}
      style={({ pressed }) => [
        styles.button,
        styles[variant],
        (disabled || loading) && styles.disabled,
        pressed && !disabled ? styles.pressed : null,
        style
      ]}
    >
      {loading ? <ActivityIndicator color="#ffffff" /> : <Text style={styles.text}>{title}</Text>}
    </Pressable>
  );
}

const styles = StyleSheet.create({
  button: {
    alignItems: "center",
    borderRadius: 12,
    minHeight: 50,
    justifyContent: "center",
    paddingHorizontal: 18
  },
  primary: {
    backgroundColor: "#2563eb"
  },
  secondary: {
    backgroundColor: "#475569"
  },
  danger: {
    backgroundColor: "#dc2626"
  },
  disabled: {
    opacity: 0.55
  },
  pressed: {
    opacity: 0.82
  },
  text: {
    color: "#ffffff",
    fontSize: 16,
    fontWeight: "700"
  }
});
