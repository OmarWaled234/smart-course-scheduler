import { StyleSheet, Text, View } from "react-native";
import { END_HOUR, HOUR_HEIGHT, START_HOUR } from "@/lib/timeUtils";
import { DayName, ScheduleBlock as ScheduleBlockType } from "@/types/schedule";
import { ScheduleBlock } from "./ScheduleBlock";

type DayColumnProps = {
  day: DayName;
  blocks: ScheduleBlockType[];
  onBlockPress?: (block: ScheduleBlockType) => void;
};

export function DayColumn({ day, blocks, onBlockPress }: DayColumnProps) {
  return (
    <View style={styles.column}>
      <Text numberOfLines={1} style={styles.day}>
        {day.slice(0, 3)}
      </Text>
      <View style={styles.hours}>
        {Array.from({ length: END_HOUR - START_HOUR }).map((_, index) => (
          <View key={index} style={styles.hourLine} />
        ))}
        {blocks.map((block) => (
          <ScheduleBlock key={block.id} block={block} onPress={onBlockPress} />
        ))}
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  column: {
    width: 112
  },
  day: {
    color: "#0f172a",
    fontSize: 13,
    fontWeight: "800",
    marginBottom: 8,
    textAlign: "center"
  },
  hours: {
    backgroundColor: "#ffffff",
    borderColor: "#e2e8f0",
    borderLeftWidth: 1,
    height: (END_HOUR - START_HOUR) * HOUR_HEIGHT,
    position: "relative"
  },
  hourLine: {
    borderBottomColor: "#edf2f7",
    borderBottomWidth: 1,
    height: HOUR_HEIGHT
  }
});
