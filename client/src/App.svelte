<script>
    import { Background, Controls, MiniMap, SvelteFlow } from "@xyflow/svelte";
    import "@xyflow/svelte/dist/style.css";

    import { onMount } from "svelte";
    import { writable } from "svelte/store";
    let entities = [];
    let links = [];
    let newEntityType = "";
    let newEntityProps = "";
    let selectedEntityA = "";
    let selectedEntityB = "";
    let newLinkType = "";
    let apiBase = "http://localhost:5000";

    let nodes = writable([]);
    let edges = writable([]);

    function entityToString(entity) {
        console.log("Converting entity to string:", entity);
        switch (entity.type) {
            case "person":
                return `🗣️ ${entity.properties.first_name || "Unknown"}`;
            case "phone":
                return `📞 ${entity.properties.number || "Unknown"}`;
            case "vehicle":
                return `🚗 ${entity.properties.license_plate || "Unknown"} (${entity.properties.model || "Unknown make"}, ${entity.properties.year || "Unknown year"})`;
            default:
                return `${entity.type} (${entity.id})`;
        }
    }

    function entityToStringByGUID(guid) {
        const entity = entities.find((e) => e.id === guid);
        return entity ? entityToString(entity) : `Unknown Entity (${guid})`;
    }

    $: nodes.set(
        entities.map((e, idx) => {
            let x = 100 * idx, y = 100 * idx;
            if (typeof e.properties._node_coordinates === "string") {
                const [sx, sy] = e.properties._node_coordinates.split(",");
                if (!isNaN(Number(sx)) && !isNaN(Number(sy))) {
                    x = Number(sx);
                    y = Number(sy);
                }
            }
            return {
                id: String(e.id),
                position: { x, y },
                data: { label: entityToString(e) }
            };
        })
    );

    $: edges.set(
        links.map((l) => ({
            id: String(l.id),
            source: String(l.entity_a),
            target: String(l.entity_b),
            label: l.link_type || "link"
        }))
    );

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
        newEntityProps.split(",").forEach((pair) => {
            const [k, v] = pair.split(":").map((s) => s && s.trim());
            if (k) props[k] = v || "";
        });
        await fetch(`${apiBase}/entities`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ type: newEntityType, properties: props }),
        });
        newEntityType = "";
        newEntityProps = "";
        await fetchEntities();
    }

    async function createLink() {
        if (!selectedEntityA || !selectedEntityB) return;
        await fetch(`${apiBase}/links`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                entity_a: selectedEntityA,
                entity_b: selectedEntityB,
                link_type: newLinkType || undefined,
            }),
        });
        selectedEntityA = "";
        selectedEntityB = "";
        newLinkType = "";
        await fetchLinks();
    }

    async function deleteEntity(id) {
        await fetch(`${apiBase}/entities/${id}`, { method: "DELETE" });
        await fetchEntities();
        await fetchLinks();
    }

    async function updateEntityPosition(id, x, y) {
        console.log(`Updating entity ${id} position to (${x}, ${y})`);
        await fetch(`${apiBase}/entities/${id}`, {
            method: "PATCH",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ _node_coordinates: `${x},${y}` })
        });
    }

    function handleNodeDragStop(event) {
        // event.detail.nodes is an array of moved nodes
        console.log("Node drag stopped:", event);
        const movedNodes = event.nodes || [];
        movedNodes.forEach((node) => {
            updateEntityPosition(node.id, node.position.x, node.position.y);
        });
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
        <input
            placeholder="Type (e.g. person, phone)"
            bind:value={newEntityType}
        />
        <input
            placeholder="Properties (key:value,...)"
            bind:value={newEntityProps}
        />
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
        <input
            placeholder="Link type (optional)"
            bind:value={newLinkType}
        />
        <button on:click={createLink}>Link</button>
    </section>

    <section>
        <h2>Entities</h2>
        <table border="1">
            <thead>
                <tr
                    ><th>ID</th><th>Type</th><th>Properties</th><th>Actions</th
                    ></tr
                >
            </thead>
            <tbody>
                {#each entities as e}
                    <tr>
                        <td>{e.id}</td>
                        <td>{e.type}</td>
                        <td>{JSON.stringify(e.properties)}</td>
                        <td
                            ><button on:click={() => deleteEntity(e.id)}
                                >Delete</button
                            ></td
                        >
                    </tr>
                {/each}
            </tbody>
        </table>
    </section>

    <section>
        <h2>Links</h2>
        <table border="1">
            <thead>
                <tr
                    ><th>ID</th><th>Entity A</th><th>Entity B</th><th>Type</th
                    ></tr
                >
            </thead>
            <tbody>
                {#each links as l}
                    <tr>
                        <td>{l.id}</td>
                        <td>{entityToStringByGUID(l.entity_a)}</td>
                        <td>{entityToStringByGUID(l.entity_b)}</td>
                        <td>{l.link_type}</td>
                    </tr>
                {/each}
            </tbody>
        </table>
    </section>
</main>
<div
    style:width="100%"
    style:height="512px"
    style:border="1px solid #ccc"
>
    <SvelteFlow
        colorMode="dark"
        colorModeSSR="dark"
        nodes={$nodes}
        edges={$edges}
        onnodedragstop={handleNodeDragStop}
    >
     <MiniMap />
    <Controls />
    <Background />
    </SvelteFlow>
</div>

<style>
    /* main {
        max-width: 900px;
        margin: 2rem auto;
        font-family: sans-serif;
    } */
    /* section {
        margin-bottom: 2rem;
    }
    input,
    select {
        margin: 0.2rem;
    }
    table {
        width: 100%;
        border-collapse: collapse;
    }
    th,
    td {
        padding: 0.3rem 0.5rem;
    }
    th {
        background: #000;
    } */
</style>
