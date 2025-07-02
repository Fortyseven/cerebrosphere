<script>
  import { onMount } from 'svelte';
  let entities = [];
  let links = [];
  let newEntityType = '';
  let newEntityProps = '';
  let selectedEntityA = '';
  let selectedEntityB = '';
  let newLinkType = '';
  let apiBase = 'http://localhost:5000';

  async function fetchEntities() {
    const res = await fetch(`${apiBase}/entities`);
    entities = await res.json();
  }
  async function fetchLinks() {
    const res = await fetch(`${apiBase}/links`);
    links = await res.json();
  }
  async function createEntity() {
    const props = {};
    newEntityProps.split(',').forEach(pair => {
      const [k, v] = pair.split(':').map(s => s && s.trim());
      if (k) props[k] = v || '';
    });
    await fetch(`${apiBase}/entities`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ type: newEntityType, properties: props })
    });
    newEntityType = '';
    newEntityProps = '';
    await fetchEntities();
  }
  async function createLink() {
    if (!selectedEntityA || !selectedEntityB) return;
    await fetch(`${apiBase}/links`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ entity_a: selectedEntityA, entity_b: selectedEntityB, link_type: newLinkType || undefined })
    });
    selectedEntityA = '';
    selectedEntityB = '';
    newLinkType = '';
    await fetchLinks();
  }
  async function deleteEntity(id) {
    await fetch(`${apiBase}/entities/${id}`, { method: 'DELETE' });
    await fetchEntities();
    await fetchLinks();
  }
  onMount(async () => {
    await fetchEntities();
    await fetchLinks();
  });
</script>

<main>
  <h1>Cerebrosphere Debug Dashboard</h1>

  <section>
    <h2>Create Entity</h2>
    <input placeholder="Type (e.g. person, phone)" bind:value={newEntityType} />
    <input placeholder="Properties (key:value,...)" bind:value={newEntityProps} />
    <button on:click={createEntity}>Create</button>
  </section>

  <section>
    <h2>Link Entities</h2>
    <select bind:value={selectedEntityA}>
      <option value="">-- Entity A --</option>
      {#each entities as e}
        <option value={e.id}>{e.type} ({e.id})</option>
      {/each}
    </select>
    <select bind:value={selectedEntityB}>
      <option value="">-- Entity B --</option>
      {#each entities as e}
        <option value={e.id}>{e.type} ({e.id})</option>
      {/each}
    </select>
    <input placeholder="Link type (optional)" bind:value={newLinkType} />
    <button on:click={createLink}>Link</button>
  </section>

  <section>
    <h2>Entities</h2>
    <table border="1">
      <thead>
        <tr><th>ID</th><th>Type</th><th>Properties</th><th>Actions</th></tr>
      </thead>
      <tbody>
        {#each entities as e}
          <tr>
            <td>{e.id}</td>
            <td>{e.type}</td>
            <td>{JSON.stringify(e.properties)}</td>
            <td><button on:click={() => deleteEntity(e.id)}>Delete</button></td>
          </tr>
        {/each}
      </tbody>
    </table>
  </section>

  <section>
    <h2>Links</h2>
    <table border="1">
      <thead>
        <tr><th>ID</th><th>Entity A</th><th>Entity B</th><th>Type</th></tr>
      </thead>
      <tbody>
        {#each links as l}
          <tr>
            <td>{l.id}</td>
            <td>{l.entity_a}</td>
            <td>{l.entity_b}</td>
            <td>{l.link_type}</td>
          </tr>
        {/each}
      </tbody>
    </table>
  </section>
</main>

<style>
  main { max-width: 900px; margin: 2rem auto; font-family: sans-serif; }
  section { margin-bottom: 2rem; }
  input, select { margin: 0.2rem; }
  table { width: 100%; border-collapse: collapse; }
  th, td { padding: 0.3rem 0.5rem; }
  th { background: #eee; }
</style>
