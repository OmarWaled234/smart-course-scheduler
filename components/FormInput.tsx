import { StyleSheet, Text, TextInput, TextInputProps, View } from "react-native";

type FormInputProps = TextInputProps & {
  label: string;
};

export function FormInput({ label, style, ...props }: FormInputProps) {
  return (
    <View style={styles.field}>
      <Text style={styles.label}>{label}</Text>
      <TextInput
        placeholderTextColor="#94a3b8"
        style={[styles.input, style]}
        autoCapitalize="none"
        {...props}
      />
    </View>
  );
}

const styles = StyleSheet.create({
  field: {
    gap: 8
  },
  label: {
    color: "#334155",
    fontSize: 14,
    fontWeight: "700"
  },
  input: {
    backgroundColor: "#ffffff",
    borderColor: "#dbe3ef",
    borderRadius: 12,
    borderWidth: 1,
    color: "#0f172a",
    fontSize: 16,
    minHeight: 50,
    paddingHorizontal: 14
  }
});
