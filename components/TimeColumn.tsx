import { StyleSheet, Text, View } from "react-native";
import { buildHourLabels, HOUR_HEIGHT } from "@/lib/timeUtils";

export function TimeColumn() {
  return (
    <View style={styles.column}>
      {buildHourLabels().map((label) => (
        <View key={label} style={styles.slot}>
          <Text style={styles.label}>{label}</Text>
        </View>
      ))}
    </View>
  );
}

const styles = StyleSheet.create({
  column: {
    width: 58
  },
  slot: {
    height: HOUR_HEIGHT,
    paddingRight: 8
  },
  label: {
    color: "#64748b",
    fontSize: 12,
    textAlign: "right"
  }
});
