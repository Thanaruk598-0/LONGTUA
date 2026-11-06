import { useEffect, useMemo, useState } from 'react';
import {
  ActivityIndicator,
  Alert,
  Pressable,
  ScrollView,
  StyleSheet,
  TextInput,
  View,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';

import { ThemedText } from '@/components/themed-text';
import { ThemedView } from '@/components/themed-view';
import { BottomTabInset, MaxContentWidth, Spacing } from '@/constants/theme';
import {
  Activity,
  cancelActivity,
  createActivity,
  createPreview,
  getAccessToken,
  getActivities,
  getSchedule,
  login,
  logout,
  Preview,
  reviewProposal,
  Schedule,
} from '@/lib/api';

const formatTime = (value: string) =>
  new Date(value).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });

const formatDate = (value: Date) =>
  value.toLocaleDateString('th-TH', { weekday: 'long', day: 'numeric', month: 'long' });

export default function HomeScreen() {
  const [token, setToken] = useState<string | null>(null);
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [activities, setActivities] = useState<Activity[]>([]);
  const [schedule, setSchedule] = useState<Schedule | null>(null);
  const [newTitle, setNewTitle] = useState('');
  const [planText, setPlanText] = useState('');
  const [preview, setPreview] = useState<Preview | null>(null);
  const [busy, setBusy] = useState(false);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const today = useMemo(() => new Date(), []);
  const scheduledIds = useMemo(
    () => new Set((schedule?.items ?? []).map((item) => item.planningObjectId)),
    [schedule],
  );
  const unscheduledActivities = activities.filter((activity) => !scheduledIds.has(activity.id));

  const refresh = async (accessToken: string) => {
    const [nextActivities, nextSchedule] = await Promise.all([
      getActivities(accessToken),
      getSchedule(accessToken),
    ]);
    setActivities(nextActivities);
    setSchedule(nextSchedule);
    setError(null);
  };

  useEffect(() => {
    getAccessToken()
      .then(async (savedToken) => {
        if (savedToken) {
          setToken(savedToken);
          await refresh(savedToken);
        }
      })
      .catch(() => setError('ไม่สามารถโหลดข้อมูลเริ่มต้นได้'))
      .finally(() => setLoading(false));
  }, []);

  const run = async (operation: () => Promise<void>) => {
    setBusy(true);
    try {
      await operation();
    } catch (operationError) {
      const message = operationError instanceof Error ? operationError.message : 'เกิดข้อผิดพลาด';
      setError(message);
      Alert.alert('ดำเนินการไม่สำเร็จ', message);
    } finally {
      setBusy(false);
    }
  };

  if (loading) {
    return (
      <ThemedView style={styles.centered}>
        <ActivityIndicator />
        <ThemedText themeColor="textSecondary">กำลังโหลด LONGTUA...</ThemedText>
      </ThemedView>
    );
  }

  if (!token) {
    return (
      <ThemedView style={styles.centered}>
        <SafeAreaView style={styles.loginCard}>
          <View style={styles.brandMark}><ThemedText style={styles.brandMarkText}>L</ThemedText></View>
          <ThemedText type="title" style={styles.loginTitle}>LONGTUA</ThemedText>
          <ThemedText themeColor="textSecondary" style={styles.centerText}>
            วางแผนวันของคุณให้เป็นระบบ
          </ThemedText>
          <TextInput
            autoCapitalize="none"
            keyboardType="email-address"
            placeholder="อีเมล"
            value={email}
            onChangeText={setEmail}
            style={styles.input}
          />
          <TextInput
            secureTextEntry
            placeholder="รหัสผ่าน"
            value={password}
            onChangeText={setPassword}
            style={styles.input}
          />
          <Pressable
            style={styles.primaryButton}
            disabled={busy}
            onPress={() => run(async () => {
              await login(email, password);
              const nextToken = await getAccessToken();
              if (!nextToken) throw new Error('ไม่พบ access token');
              setToken(nextToken);
              await refresh(nextToken);
            })}>
            <ThemedText style={styles.buttonText}>{busy ? 'กำลังเข้าสู่ระบบ...' : 'เข้าสู่ระบบ'}</ThemedText>
          </Pressable>
          {error && <ThemedText style={styles.errorText}>{error}</ThemedText>}
        </SafeAreaView>
      </ThemedView>
    );
  }

  const currentScheduleItems = schedule?.items ?? [];

  return (
    <ThemedView style={styles.container}>
      <SafeAreaView style={styles.safeArea}>
        <ScrollView contentContainerStyle={styles.content} showsVerticalScrollIndicator={false}>
          <View style={styles.header}>
            <View>
              <ThemedText themeColor="textSecondary" type="small">ตารางของฉัน</ThemedText>
              <ThemedText type="subtitle">วันนี้</ThemedText>
            </View>
            <Pressable onPress={() => run(async () => { await logout(); setToken(null); })}>
              <ThemedText type="linkPrimary">ออกจากระบบ</ThemedText>
            </Pressable>
          </View>

          <ThemedText themeColor="textSecondary">{formatDate(today)}</ThemedText>
          {error && (
            <View style={styles.errorBanner}>
              <ThemedText style={styles.errorText}>{error}</ThemedText>
              <Pressable onPress={() => run(() => refresh(token))}><ThemedText type="linkPrimary">ลองใหม่</ThemedText></Pressable>
            </View>
          )}

          <View style={styles.statsRow}>
            <View style={styles.statCard}><ThemedText style={styles.statNumber}>{currentScheduleItems.length}</ThemedText><ThemedText themeColor="textSecondary" type="small">จัดไว้แล้ว</ThemedText></View>
            <View style={styles.statCard}><ThemedText style={styles.statNumber}>{unscheduledActivities.length}</ThemedText><ThemedText themeColor="textSecondary" type="small">ยังไม่จัดเวลา</ThemedText></View>
            <View style={styles.statCard}><ThemedText style={styles.statNumber}>V{schedule?.scheduleVersion?.versionNumber ?? 0}</ThemedText><ThemedText themeColor="textSecondary" type="small">เวอร์ชัน</ThemedText></View>
          </View>

          <SectionTitle title="ตารางวันนี้" subtitle="Confirmed Schedule" />
          {currentScheduleItems.length === 0 ? (
            <EmptyState title="วันนี้ยังไม่มีตาราง" action="เพิ่มกิจกรรมหรือวางแผนด้านล่าง" />
          ) : (
            currentScheduleItems.map((item) => {
              const activity = activities.find((candidate) => candidate.id === item.planningObjectId);
              return (
                <View style={styles.timelineRow} key={item.id}>
                  <ThemedText type="smallBold" themeColor="textSecondary" style={styles.timeLabel}>{formatTime(item.startAt)}</ThemedText>
                  <View style={styles.timelineLine}><View style={styles.timelineDot} /></View>
                  <ThemedView type="backgroundElement" style={styles.eventCard}>
                    <ThemedText type="smallBold">{activity?.title ?? 'กิจกรรม'}</ThemedText>
                    <ThemedText type="small" themeColor="textSecondary">{formatTime(item.startAt)} - {formatTime(item.endAt)}</ThemedText>
                  </ThemedView>
                </View>
              );
            })
          )}

          <SectionTitle title="All Day / ยังไม่จัดเวลา" subtitle="Activities" />
          {unscheduledActivities.length === 0 ? (
            <EmptyState title="ไม่มีรายการค้าง" action="กิจกรรมทั้งหมดถูกจัดลงตารางแล้ว" />
          ) : unscheduledActivities.map((activity) => (
            <ThemedView type="backgroundElement" style={styles.activityCard} key={activity.id}>
              <View style={styles.activityInfo}>
                <View style={styles.activityDot} />
                <View><ThemedText type="smallBold">{activity.title}</ThemedText><ThemedText type="small" themeColor="textSecondary">{activity.durationMinutes ? `${activity.durationMinutes} นาที` : 'ยังไม่กำหนดเวลา'}</ThemedText></View>
              </View>
              <Pressable onPress={() => run(async () => { await cancelActivity(token, activity.id); await refresh(token); })}>
                <ThemedText type="linkPrimary">ยกเลิก</ThemedText>
              </Pressable>
            </ThemedView>
          ))}

          <SectionTitle title="เพิ่มกิจกรรม" subtitle="ไม่ต้องกรอกข้อมูลทั้งหมดก็ได้" />
          <TextInput placeholder="เช่น อ่านหนังสือ หรือทำรายงาน" value={newTitle} onChangeText={setNewTitle} style={styles.input} />
          <Pressable style={styles.primaryButton} disabled={busy || !newTitle.trim()} onPress={() => run(async () => {
            await createActivity(token, newTitle.trim());
            setNewTitle('');
            await refresh(token);
          })}><ThemedText style={styles.buttonText}>+ เพิ่มกิจกรรม</ThemedText></Pressable>

          <SectionTitle title="วางแผน" subtitle="Planning Proposal" />
          <TextInput placeholder="เช่น จัดตารางกิจกรรมของฉันวันนี้" value={planText} onChangeText={setPlanText} style={[styles.input, styles.planInput]} multiline />
          <Pressable style={styles.secondaryButton} disabled={busy} onPress={() => run(async () => {
            const nextPreview = await createPreview(token, planText.trim() || 'จัดตารางกิจกรรมของฉัน');
            setPreview(nextPreview);
          })}><ThemedText>สร้างข้อเสนอแผน</ThemedText></Pressable>

          {preview && (
            <View style={styles.proposalCard}>
              <View style={styles.proposalHeader}><View><ThemedText type="smallBold">ข้อเสนอแผนใหม่</ThemedText><ThemedText type="small" themeColor="textSecondary">ยังไม่เปลี่ยนตารางปัจจุบัน</ThemedText></View><View style={styles.pendingBadge}><ThemedText type="smallBold" style={styles.pendingText}>PENDING</ThemedText></View></View>
              {preview.candidateItems.map((item) => <View style={styles.previewItem} key={item.planningObjectId}><ThemedText type="smallBold">{item.title}</ThemedText><ThemedText type="small" themeColor="textSecondary">{formatTime(item.startAt)} - {formatTime(item.endAt)}</ThemedText></View>)}
              <View style={styles.actions}>
                <Pressable style={styles.primaryButton} onPress={() => run(async () => { await reviewProposal(token, preview.proposalId, 'confirm'); setPreview(null); await refresh(token); })}><ThemedText style={styles.buttonText}>ยืนยันแผน</ThemedText></Pressable>
                <Pressable style={styles.secondaryButton} onPress={() => run(async () => { await reviewProposal(token, preview.proposalId, 'reject'); setPreview(null); })}><ThemedText>ปฏิเสธ</ThemedText></Pressable>
              </View>
            </View>
          )}
        </ScrollView>
      </SafeAreaView>
    </ThemedView>
  );
}

function SectionTitle({ title, subtitle }: { title: string; subtitle: string }) {
  return <View style={styles.sectionTitle}><ThemedText type="subtitle" style={styles.sectionHeading}>{title}</ThemedText><ThemedText type="small" themeColor="textSecondary">{subtitle}</ThemedText></View>;
}

function EmptyState({ title, action }: { title: string; action: string }) {
  return <ThemedView type="backgroundElement" style={styles.emptyState}><ThemedText type="smallBold">{title}</ThemedText><ThemedText type="small" themeColor="textSecondary">{action}</ThemedText></ThemedView>;
}

const styles = StyleSheet.create({
  container: { flex: 1 },
  centered: { flex: 1, alignItems: 'center', justifyContent: 'center', padding: Spacing.four, gap: Spacing.three },
  safeArea: { flex: 1, paddingHorizontal: Spacing.three, paddingBottom: BottomTabInset, maxWidth: MaxContentWidth, width: '100%', alignSelf: 'center' },
  content: { gap: Spacing.three, paddingVertical: Spacing.three },
  loginCard: { flex: 1, justifyContent: 'center', gap: Spacing.three, paddingHorizontal: Spacing.four, width: '100%' },
  brandMark: { width: 56, height: 56, borderRadius: 18, backgroundColor: '#2563eb', alignItems: 'center', justifyContent: 'center', alignSelf: 'center' },
  brandMarkText: { color: '#fff', fontSize: 32, fontWeight: '700' },
  loginTitle: { textAlign: 'center', fontSize: 36 },
  centerText: { textAlign: 'center' },
  header: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center' },
  statsRow: { flexDirection: 'row', gap: Spacing.two },
  statCard: { flex: 1, padding: Spacing.three, borderRadius: Spacing.three, backgroundColor: '#eef4ff', gap: Spacing.one },
  statNumber: { color: '#2563eb', fontSize: 22, fontWeight: '700' },
  sectionTitle: { marginTop: Spacing.two, gap: Spacing.one },
  sectionHeading: { fontSize: 24, lineHeight: 30 },
  timelineRow: { flexDirection: 'row', alignItems: 'stretch', minHeight: 72 },
  timeLabel: { width: 52, paddingTop: Spacing.two },
  timelineLine: { width: 20, alignItems: 'center', paddingTop: Spacing.three },
  timelineDot: { width: 10, height: 10, borderRadius: 5, backgroundColor: '#2563eb' },
  eventCard: { flex: 1, padding: Spacing.three, borderRadius: Spacing.three, gap: Spacing.one, borderLeftWidth: 3, borderLeftColor: '#2563eb' },
  activityCard: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', padding: Spacing.three, borderRadius: Spacing.three },
  activityInfo: { flexDirection: 'row', alignItems: 'center', gap: Spacing.two },
  activityDot: { width: 10, height: 10, borderRadius: 5, backgroundColor: '#f59e0b' },
  emptyState: { padding: Spacing.four, borderRadius: Spacing.three, gap: Spacing.one },
  input: { borderWidth: 1, borderColor: '#d1d5db', borderRadius: Spacing.two, paddingHorizontal: Spacing.three, paddingVertical: Spacing.two, backgroundColor: '#fff', fontSize: 16 },
  planInput: { minHeight: 64, textAlignVertical: 'top' },
  primaryButton: { backgroundColor: '#2563eb', borderRadius: Spacing.two, alignItems: 'center', padding: Spacing.three },
  secondaryButton: { borderWidth: 1, borderColor: '#cbd5e1', borderRadius: Spacing.two, alignItems: 'center', padding: Spacing.three },
  buttonText: { color: '#fff', fontWeight: '700' },
  errorBanner: { backgroundColor: '#fef2f2', padding: Spacing.three, borderRadius: Spacing.two, gap: Spacing.one },
  errorText: { color: '#b91c1c' },
  proposalCard: { borderWidth: 1, borderColor: '#f59e0b', borderRadius: Spacing.three, padding: Spacing.three, gap: Spacing.three, backgroundColor: '#fffbeb' },
  proposalHeader: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center' },
  pendingBadge: { backgroundColor: '#fef3c7', paddingHorizontal: Spacing.two, paddingVertical: Spacing.one, borderRadius: 999 },
  pendingText: { color: '#92400e' },
  previewItem: { borderBottomWidth: 1, borderBottomColor: '#fde68a', paddingBottom: Spacing.two, gap: Spacing.one },
  actions: { flexDirection: 'row', gap: Spacing.two },
});
