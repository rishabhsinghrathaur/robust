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

const apiBaseUrl = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000";

export function App() {
  const [devices, setDevices] = useState(fallbackDevices);
  const [summary, setSummary] = useState(fallbackSummary);
  const [loading, setLoading] = useState(true);
  const [mode, setMode] = useState("Demo data");

  useEffect(() => {
    let active = true;

    async function loadData() {
      try {
        const [devicesResponse, summaryResponse] = await Promise.all([
          fetch(`${apiBaseUrl}/devices`),
          fetch(`${apiBaseUrl}/dashboard/summary`),
        ]);

        if (!devicesResponse.ok || !summaryResponse.ok) {
          throw new Error("API request failed");
        }

        const devicesPayload = await devicesResponse.json();
        const summaryPayload = await summaryResponse.json();

        if (!active) {
          return;
        }

        setDevices(devicesPayload.devices);
        setSummary(summaryPayload);
        setMode("Live backend");
      } catch {
        if (!active) {
          return;
        }
        setMode("Demo fallback");
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
            <h2>AI Action Queue</h2>
            <span>Human approval required</span>
          </div>
          <ul className="actionList">
            {actions.map((action) => (
              <li key={action}>
                <span>{action}</span>
                <button type="button">Review</button>
              </li>
            ))}
          </ul>
        </article>
      </section>

      <section className="panel">
        <div className="panelHeader">
          <h2>Devices</h2>
          <span>Representative sample</span>
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
                <tr key={device.id}>
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
    </main>
  );
}
