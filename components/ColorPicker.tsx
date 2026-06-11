import { Pressable, StyleSheet, View } from "react-native";

const COLORS = ["#2563eb", "#16a34a", "#dc2626", "#9333ea", "#ea580c", "#0891b2", "#475569"];

type ColorPickerProps = {
  value: string;
  onChange: (color: string) => void;
};

export function ColorPicker({ value, onChange }: ColorPickerProps) {
  return (
    <View style={styles.row}>
      {COLORS.map((color) => (
        <Pressable
          accessibilityRole="button"
          accessibilityLabel={`Choose ${color}`}
          key={color}
          onPress={() => onChange(color)}
          style={[styles.swatch, { backgroundColor: color }, value === color && styles.selected]}
        />
      ))}
    </View>
  );
}

const styles = StyleSheet.create({
  row: {
    flexDirection: "row",
    flexWrap: "wrap",
    gap: 12
  },
  swatch: {
    borderRadius: 16,
    height: 32,
    width: 32
  },
  selected: {
    borderColor: "#0f172a",
    borderWidth: 3
  }
});
