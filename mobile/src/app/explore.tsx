import { Alert, Pressable, ScrollView, StyleSheet, View } from 'react-native';
import type { ReactNode } from 'react';
import { SafeAreaView } from 'react-native-safe-area-context';

import { ThemedText } from '@/components/themed-text';
import { ThemedView } from '@/components/themed-view';
import { BottomTabInset, MaxContentWidth, Spacing } from '@/constants/theme';

export default function SettingsScreen() {
  return (
    <ThemedView style={styles.container}>
      <SafeAreaView style={styles.safeArea}>
        <ScrollView contentContainerStyle={styles.content}>
          <ThemedText type="title">ตั้งค่า</ThemedText>
          <ThemedText themeColor="textSecondary">
            จัดการบัญชีและการตั้งค่าการวางแผนของคุณ
          </ThemedText>

          <SettingsSection title="บัญชี">
            <SettingRow label="ข้อมูลบัญชี" value="ดูและแก้ไขข้อมูลส่วนตัว" />
            <SettingRow label="เขตเวลา" value="ใช้เขตเวลาของบัญชี" />
          </SettingsSection>

          <SettingsSection title="การแจ้งเตือน">
            <SettingRow label="การแจ้งเตือนกิจกรรม" value="จัดการจากตารางที่ยืนยันแล้ว" />
            <SettingRow label="ช่วงเวลาที่ไม่รบกวน" value="กำลังจะเปิดใช้งาน" />
          </SettingsSection>

          <SettingsSection title="ระบบ">
            <SettingRow label="เกี่ยวกับ LONGTUA" value="Personal Adaptive Planner" />
            <Pressable
              style={styles.actionRow}
              onPress={() => Alert.alert('LONGTUA', 'Settings API จะเชื่อมต่อในขั้นตอนถัดไป')}>
              <View>
                <ThemedText type="smallBold">การตั้งค่าขั้นสูง</ThemedText>
                <ThemedText type="small" themeColor="textSecondary">
                  Availability, Notification และ Time Window
                </ThemedText>
              </View>
              <ThemedText type="linkPrimary">เร็ว ๆ นี้</ThemedText>
            </Pressable>
          </SettingsSection>
        </ScrollView>
      </SafeAreaView>
    </ThemedView>
  );
}

function SettingsSection({ title, children }: { title: string; children: ReactNode }) {
  return (
    <View style={styles.section}>
      <ThemedText type="smallBold" themeColor="textSecondary">{title}</ThemedText>
      <ThemedView type="backgroundElement" style={styles.card}>{children}</ThemedView>
    </View>
  );
}

function SettingRow({ label, value }: { label: string; value: string }) {
  return (
    <View style={styles.actionRow}>
      <View style={styles.rowText}>
        <ThemedText type="smallBold">{label}</ThemedText>
        <ThemedText type="small" themeColor="textSecondary">{value}</ThemedText>
      </View>
      <ThemedText themeColor="textSecondary">›</ThemedText>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1 },
  safeArea: {
    flex: 1,
    width: '100%',
    maxWidth: MaxContentWidth,
    alignSelf: 'center',
    paddingHorizontal: Spacing.three,
    paddingBottom: BottomTabInset,
  },
  content: { gap: Spacing.three, paddingVertical: Spacing.three },
  section: { gap: Spacing.two, marginTop: Spacing.two },
  card: { borderRadius: Spacing.three, overflow: 'hidden' },
  actionRow: {
    minHeight: 68,
    paddingHorizontal: Spacing.three,
    paddingVertical: Spacing.two,
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    borderBottomWidth: StyleSheet.hairlineWidth,
    borderBottomColor: '#cbd5e1',
  },
  rowText: { gap: Spacing.one, flex: 1 },
});
