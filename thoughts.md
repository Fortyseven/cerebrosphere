This project, Cerebrosphere, is intended to help an investigator oraganize data related to a case.

There is a Flask backend (`/server`) serving an API to a SvelteKit client frontend (`/client`).

A Workspace is a clean SQLite database.

An Entity is a node in a graph, so to speak.

Each Entity:
    - has key/value fields
    - a 'type' field
      - a specific 'type' has a preset collection of fields when created

A Link connects an Entity to other entities. For example, a "business" entity might have an 'owner' field with a link to a Location-type Entity.


Examples:

    ENTITY (Person)
        - id            => {3741938}
        - type          => 'person'
        - first_name    => 'Toby'
        - middle_name   => ''
        - last_name     => 'Deshane'
        - phone         => {908134}

    LINK -> ENTITY (Phone)
        - id          => {908134}
        - type        => 'phone'
        - value       => '8005551212'
        - phone_type  => 'mobile'

    LINK -> ENTITY (Location)
        - id          => {093148190}
        - type        => 'location'
        - city        => 'Phoenix'
        - state       => 'AZ'
        - postal      => '85001'

    ENTITY (business)
        - id        => {GUID}
        - type      => 'business'
        - name      => 'Sew Far Sew Good'
        - location  => {093148190}
        - owner     => {3741938}



Links are considered bidirectional.

Link types:
    - connected_to (default when no link type provided)
    - has
    - owns
    - located_at
    - employs
    - coworker
    - associated_with
    - parent_of
    - spouse_of
    - alias_of
    - contact_of
    - member_of
    - related_to
    - transacts_with
    - supervises
    - manages
    - friend_of
    - enemy_of
    - witnessed
    - suspect
    - victim
    - registered_to
    - uses
    - account_of
