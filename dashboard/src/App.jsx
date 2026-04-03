import { useEffect, useState } from "react";

const actions = [
  "Reboot greenhouse controller",
  "Check low-battery field devices",
  "Schedule staged OTA rollout for ESP32 fleet",
];

const fallbackDevices = [
  { id: "RB-ESP32-01", device_type: "esp32", firmware_version: "1.0.3", status: "online", site: "Lab A" },
  { id: "RB-STM32-07", device_type: "stm32", firmware_version: "1.1.0", status: "updating", site: "Field 2" },
  { id: "RB-ESP32-19", device_type: "esp32", firmware_version: "0.9.8", status: "offline", site: "Greenhouse" },
];

const fallbackSummary = {
  managed_devices: 128,
  healthy_percent: 94,
  devices_needing_attention: 8,
  active_sites: 3,
  queued_commands: 12,
  available_releases: 3,
};

const fallbackActivity = [
  { kind: "command", summary: "system queued sync-config", timestamp: "2026-04-03T12:40:00Z" },
  { kind: "release", summary: "Release 1.1.0 available for esp32", timestamp: "2026-04-03T12:15:00Z" },
];

const apiBaseUrl = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000";

export function App() {
  const [devices, setDevices] = useState(fallbackDevices);
  const [summary, setSummary] = useState(fallbackSummary);
  const [activity, setActivity] = useState(fallbackActivity);
  const [selectedDevice, setSelectedDevice] = useState(fallbackDevices[0]);
  const [selectedDetail, setSelectedDetail] = useState(null);
  const [loading, setLoading] = useState(true);
  const [mode, setMode] = useState("Demo data");

  useEffect(() => {
    let active = true;

    async function loadData() {
      try {
        const [devicesResponse, summaryResponse, activityResponse] = await Promise.all([
          fetch(`${apiBaseUrl}/devices`),
          fetch(`${apiBaseUrl}/dashboard/summary`),
          fetch(`${apiBaseUrl}/dashboard/activity`),
        ]);

        if (!devicesResponse.ok || !summaryResponse.ok || !activityResponse.ok) {
          throw new Error("API request failed");
        }

        const devicesPayload = await devicesResponse.json();
        const summaryPayload = await summaryResponse.json();
        const activityPayload = await activityResponse.json();

        if (!active) {
          return;
        }

        setDevices(devicesPayload.devices);
        setSummary(summaryPayload);
        setActivity(activityPayload.activity);
        setSelectedDevice(devicesPayload.devices[0] ?? fallbackDevices[0]);
        setMode("Live backend");
      } catch {
        if (!active) {
          return;
        }
        setMode("Demo fallback");
        setSelectedDevice(fallbackDevices[0]);
      } finally {
        if (active) {
          setLoading(false);
        }
      }
    }

    loadData();
    return () => {
      active = false;
    };
  }, []);

  useEffect(() => {
    let active = true;
    if (!selectedDevice?.id) {
      return undefined;
    }

    async function loadDeviceDetail() {
      try {
        const response = await fetch(`${apiBaseUrl}/devices/${selectedDevice.id}`);
        if (!response.ok) {
          throw new Error("detail request failed");
        }
        const payload = await response.json();
        if (active) {
          setSelectedDetail(payload);
        }
      } catch {
        if (active) {
          setSelectedDetail({
            device: selectedDevice,
            recent_commands: [
              { id: "demo-command", command: "sync-config", status: "queued", issued_by: "system" },
            ],
            telemetry: [
              {
                recorded_at: "2026-04-03T12:40:00Z",
                temperature_c: 24.1,
                battery_percent: 91,
                connectivity: "good",
                message: "Demo heartbeat",
              },
            ],
          });
        }
      }
    }

    loadDeviceDetail();
    return () => {
      active = false;
    };
  }, [selectedDevice]);

  return (
    <main className="shell">
      <section className="hero">
        <div>
          <p className="eyebrow">Robust Control Plane</p>
          <h1>Fleet control for hardware that needs more than a dashboard.</h1>
          <p className="lede">
            Provision devices, track firmware, review AI-generated actions, and keep remote
            hardware fleets stable under real-world conditions.
          </p>
        </div>
        <div className="heroPanel">
          <span className="metricValue">{summary.managed_devices}</span>
          <span className="metricLabel">Managed devices</span>
          <span className="metricDetail">
            {summary.healthy_percent}% healthy, {summary.available_releases} staged releases,{" "}
            {summary.queued_commands} queued actions
          </span>
          <span className="modeBadge">{loading ? "Loading" : mode}</span>
        </div>
      </section>

      <section className="grid">
        <article className="panel">
          <div className="panelHeader">
            <h2>Fleet Snapshot</h2>
            <span>Live overview</span>
          </div>
          <div className="stats">
            <div>
              <strong>{summary.healthy_percent}%</strong>
              <span>Healthy</span>
            </div>
            <div>
              <strong>{summary.devices_needing_attention}</strong>
              <span>Need updates</span>
            </div>
            <div>
              <strong>{summary.active_sites}</strong>
              <span>Sites active</span>
            </div>
          </div>
        </article>

        <article className="panel">
          <div className="panelHeader">
            <h2>Recent Activity</h2>
            <span>Commands and releases</span>
          </div>
          <ul className="actionList">
            {activity.map((item, index) => (
              <li key={`${item.kind}-${item.timestamp}-${index}`}>
                <span>
                  <strong>{item.kind}</strong>
                  <small>{item.summary}</small>
                </span>
                <button type="button">Inspect</button>
              </li>
            ))}
          </ul>
        </article>
      </section>

      <section className="panel">
        <div className="panelHeader">
          <h2>Devices</h2>
          <span>Select a device for detail</span>
        </div>
        <div className="tableWrap">
          <table>
            <thead>
              <tr>
                <th>ID</th>
                <th>Type</th>
                <th>Firmware</th>
                <th>Status</th>
                <th>Site</th>
              </tr>
            </thead>
            <tbody>
              {devices.map((device) => (
                <tr
                  key={device.id}
                  className={device.id === selectedDevice?.id ? "selectedRow" : ""}
                  onClick={() => setSelectedDevice(device)}
                >
                  <td>{device.device_uid ?? device.id}</td>
                  <td>{String(device.device_type).toUpperCase()}</td>
                  <td>{device.firmware_version}</td>
                  <td>
                    <span className={`status status-${device.status}`}>{device.status}</span>
                  </td>
                  <td>{device.site}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>

      <section className="grid detailGrid">
        <article className="panel">
          <div className="panelHeader">
            <h2>Device Detail</h2>
            <span>{selectedDevice?.device_uid ?? selectedDevice?.id ?? "No selection"}</span>
          </div>
          <div className="detailCard">
            <div>
              <strong>Site</strong>
              <span>{selectedDetail?.device?.site ?? selectedDevice?.site}</span>
            </div>
            <div>
              <strong>Firmware</strong>
              <span>{selectedDetail?.device?.firmware_version ?? selectedDevice?.firmware_version}</span>
            </div>
            <div>
              <strong>Status</strong>
              <span>{selectedDetail?.device?.status ?? selectedDevice?.status}</span>
            </div>
            <div>
              <strong>Last Seen</strong>
              <span>{selectedDetail?.device?.last_seen_at ?? "n/a"}</span>
            </div>
          </div>
        </article>

        <article className="panel">
          <div className="panelHeader">
            <h2>AI Action Queue</h2>
            <span>Human approval required</span>
          </div>
          <ul className="actionList">
            {actions.map((action) => (
              <li key={action}>
                <span>
                  <strong>suggested</strong>
                  <small>{action}</small>
                </span>
                <button type="button">Review</button>
              </li>
            ))}
          </ul>
        </article>
      </section>

      <section className="grid detailGrid">
        <article className="panel">
          <div className="panelHeader">
            <h2>Recent Commands</h2>
            <span>Selected device</span>
          </div>
          <ul className="detailList">
            {(selectedDetail?.recent_commands ?? []).map((command) => (
              <li key={command.id}>
                <strong>{command.command}</strong>
                <span>{command.issued_by} · {command.status}</span>
              </li>
            ))}
          </ul>
        </article>

        <article className="panel">
          <div className="panelHeader">
            <h2>Telemetry</h2>
            <span>Latest samples</span>
          </div>
          <ul className="detailList">
            {(selectedDetail?.telemetry ?? []).map((entry, index) => (
              <li key={`${entry.recorded_at}-${index}`}>
                <strong>{entry.temperature_c ?? "--"}C / {entry.battery_percent ?? "--"}%</strong>
                <span>{entry.connectivity} · {entry.message ?? "heartbeat"}</span>
              </li>
            ))}
          </ul>
        </article>
      </section>
    </main>
  );
}
