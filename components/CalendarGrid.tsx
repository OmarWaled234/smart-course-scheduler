import { ScrollView, StyleSheet, View } from "react-native";
import { DAYS, ScheduleBlock as ScheduleBlockType } from "@/types/schedule";
import { DayColumn } from "./DayColumn";
import { TimeColumn } from "./TimeColumn";

type CalendarGridProps = {
  blocks: ScheduleBlockType[];
  onBlockPress?: (block: ScheduleBlockType) => void;
};

export function CalendarGrid({ blocks, onBlockPress }: CalendarGridProps) {
  return (
    <ScrollView style={styles.container}>
      <View style={styles.headerSpacer} />
      <ScrollView horizontal showsHorizontalScrollIndicator={false}>
        <View style={styles.row}>
          <TimeColumn />
          {DAYS.map((day) => (
            <DayColumn
              key={day}
              day={day}
              blocks={blocks.filter((block) => block.day === day)}
              onBlockPress={onBlockPress}
            />
          ))}
        </View>
      </ScrollView>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1
  },
  headerSpacer: {
    height: 2
  },
  row: {
    flexDirection: "row",
    paddingBottom: 24
  }
});
