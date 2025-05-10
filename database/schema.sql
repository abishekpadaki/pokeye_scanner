-- schema.sql for Pokeye Scanner

-- Drop table if it exists to ensure a clean slate (optional, use with caution)
-- DROP TABLE IF EXISTS pokemon_cards CASCADE;

-- Main table for storing Pokémon card information
CREATE TABLE pokemon_cards (
    id SERIAL PRIMARY KEY,                -- Unique identifier for each card entry
    scan_timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP, -- When the card was scanned
    
    card_name VARCHAR(255) NOT NULL,    -- Name of the Pokémon
    hp INTEGER,                         -- Hit Points
    pokemon_type JSONB,                 -- Array of Pokémon types (e.g., ["Grass", "Poison"])
    evolves_from VARCHAR(255),          -- Name of the Pokémon it evolves from
    
    attacks JSONB,                      -- Array of attack objects, e.g., 
                                        -- [{"name": "Vine Whip", "cost": ["Grass"], "damage": "10", "description": "..."}]
    
    weakness_type VARCHAR(100),         -- Type of weakness (e.g., "Fire")
    weakness_value VARCHAR(50),         -- Value of weakness (e.g., "x2")
    
    resistance_type VARCHAR(100),       -- Type of resistance (e.g., "Water")
    resistance_value VARCHAR(50),       -- Value of resistance (e.g., "-30")
    
    retreat_cost JSONB,                 -- Array of energy types for retreat cost (e.g., ["Colorless", "Colorless"])
    
    card_number VARCHAR(50),            -- Card number in the set (e.g., "58/102")
    rarity VARCHAR(100),                -- Rarity of the card (e.g., "Common", "Holo Rare")
    illustrator VARCHAR(255),           -- Name of the card illustrator
    set_name VARCHAR(255),              -- Name of the Pokémon TCG set
    
    additional_info TEXT,               -- For any other text, abilities, Pokédex entries, etc.
    
    image_filename VARCHAR(255),        -- Filename of the scanned image (if stored locally by backend)
    llm_raw_response JSONB              -- The raw JSON response from the LLM for audit/debugging
);

-- Optional: Indexes for frequently queried columns
CREATE INDEX IF NOT EXISTS idx_card_name ON pokemon_cards(card_name);
CREATE INDEX IF NOT EXISTS idx_set_name ON pokemon_cards(set_name);
CREATE INDEX IF NOT EXISTS idx_pokemon_type ON pokemon_cards USING GIN(pokemon_type); -- GIN index for JSONB array

-- Example of how you might insert data (for backend reference):
/*
INSERT INTO pokemon_cards (
    card_name, hp, pokemon_type, evolves_from, attacks, 
    weakness_type, weakness_value, resistance_type, resistance_value, retreat_cost, 
    card_number, rarity, illustrator, set_name, additional_info, image_filename, llm_raw_response
) VALUES (
    'Pikachu', 60, '["Lightning"]'::jsonb, NULL, 
    '[{"name": "Gnaw", "cost": ["Colorless"], "damage": "10", "description": ""}, {"name": "Thunder Jolt", "cost": ["Lightning", "Colorless"], "damage": "30", "description": "Flip a coin. If tails, Pikachu does 10 damage to itself."}]'::jsonb, 
    'Fighting', 'x2', NULL, NULL, '["Colorless"]'::jsonb, 
    '58/102', 'Common', 'Mitsuhiro Arita', 'Base Set', 'Loves to eat apples.', 'scan_xxxxxxxx.jpg', '{ "original_llm_data": "..." }'::jsonb
);
*/

-- You can add more tables or constraints as needed.
-- For example, separate tables for sets, types, attacks if you want a more normalized database,
-- but for simplicity, JSONB fields are used here for structured but flexible data. 