const devices = [
  { id: "RB-ESP32-01", type: "ESP32", firmware: "1.0.3", status: "Online", site: "Lab A" },
  { id: "RB-STM32-07", type: "STM32", firmware: "1.1.0", status: "Updating", site: "Field 2" },
  { id: "RB-ESP32-19", type: "ESP32", firmware: "0.9.8", status: "Offline", site: "Greenhouse" },
];

const actions = [
  "Reboot greenhouse controller",
  "Check low-battery field devices",
  "Schedule staged OTA rollout for ESP32 fleet",
];

export function App() {
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
          <span className="metricValue">128</span>
          <span className="metricLabel">Managed devices</span>
          <span className="metricDetail">94% online, 3 staged OTA campaigns, 12 AI suggestions pending review</span>
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
              <strong>94%</strong>
              <span>Healthy</span>
            </div>
            <div>
              <strong>8</strong>
              <span>Need updates</span>
            </div>
            <div>
              <strong>3</strong>
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
                  <td>{device.id}</td>
                  <td>{device.type}</td>
                  <td>{device.firmware}</td>
                  <td>{device.status}</td>
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

