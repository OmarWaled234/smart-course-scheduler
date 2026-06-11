import { Pressable, StyleSheet, Text } from "react-native";
import { getBlockLayout } from "@/lib/timeUtils";
import { ScheduleBlock as ScheduleBlockType } from "@/types/schedule";

type ScheduleBlockProps = {
  block: ScheduleBlockType;
  onPress?: (block: ScheduleBlockType) => void;
};

export function ScheduleBlock({ block, onPress }: ScheduleBlockProps) {
  const layout = getBlockLayout(block.start_time, block.end_time);

  return (
    <Pressable
      onPress={() => onPress?.(block)}
      style={[styles.block, { backgroundColor: block.color, top: layout.top, height: layout.height }]}
    >
      <Text numberOfLines={1} style={styles.title}>
        {block.title}
      </Text>
      <Text numberOfLines={1} style={styles.meta}>
        {block.start_time} - {block.end_time}
      </Text>
      {!!block.location && (
        <Text numberOfLines={1} style={styles.meta}>
          {block.location}
        </Text>
      )}
    </Pressable>
  );
}

const styles = StyleSheet.create({
  block: {
    borderRadius: 8,
    left: 4,
    padding: 7,
    position: "absolute",
    right: 4
  },
  title: {
    color: "#ffffff",
    fontSize: 12,
    fontWeight: "800"
  },
  meta: {
    color: "#e2e8f0",
    fontSize: 10,
    marginTop: 2
  }
});
