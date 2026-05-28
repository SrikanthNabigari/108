-- Migration 002: Fix Moon longitude in birth_charts
-- The stored value (326.85) was incorrect. Swiss Ephemeris computes 324.1124
-- for birth: 1992-12-03 03:00:00 IST, 16.726239N, 81.288428E.
-- This 2.74 degree error shifts the entire Vimshottari dasha chain by ~3 years.
--
-- Correct values:
--   Moon longitude: 324.11243435123794
--   Nakshatra: Purva Bhadrapada, Pada 2 (was stored as Pada 3)
--   Moon Rashi: Aquarius (unchanged)

-- Update the moon longitude inside the planets JSONB column
-- and fix moon_nakshatra_pada for all affected users
UPDATE birth_charts
SET
    planets = jsonb_set(
        planets,
        '{moon,longitude}',
        '324.11243435123794'::jsonb
    ),
    moon_nakshatra_pada = 2,
    calculated_at = NOW()
WHERE
    planets->'moon'->>'longitude' = '326.85'
    OR (planets->'moon'->'longitude')::text::float BETWEEN 326.84 AND 326.86;

-- Also update via full planet recalculation for specific known user IDs
-- Gateway DEV_USER_ID
UPDATE birth_charts
SET
    planets = '{"sun": {"longitude": 227.21541798409706, "latitude": 0.0001595870524741406, "speed": 1.0141951406011571, "is_retrograde": false}, "moon": {"longitude": 324.11243435123794, "latitude": 5.267392152494375, "speed": 11.91565766227218, "is_retrograde": false}, "mars": {"longitude": 93.75873633864964, "latitude": 2.6408767817797694, "speed": -0.05407388494581116, "is_retrograde": true}, "mercury": {"longitude": 208.66090321436045, "latitude": 2.6431272017471428, "speed": 0.2650709864263216, "is_retrograde": false}, "jupiter": {"longitude": 166.2398881945757, "latitude": 1.1968295326580562, "speed": 0.15106373650827554, "is_retrograde": false}, "venus": {"longitude": 269.3542913956311, "latitude": -2.339997114516735, "speed": 1.1826124101959332, "is_retrograde": false}, "saturn": {"longitude": 289.9336238105079, "latitude": -1.0167093934794378, "speed": 0.07496863933039054, "is_retrograde": false}, "rahu": {"longitude": 238.20830581751625, "latitude": 0.0, "speed": -0.05297152198333536, "is_retrograde": true}, "ketu": {"longitude": 58.20830581751625, "latitude": -0.0, "speed": -0.05297152198333536, "is_retrograde": true}}'::jsonb,
    moon_nakshatra_pada = 2,
    calculated_at = NOW()
WHERE user_id IN (
    '42527e69-bd1b-4c09-a57c-ef3785f0f7d1'::uuid,
    'e0668425-3ae7-4567-baa1-fb659666622e'::uuid
);

-- Verify
SELECT user_id,
       planets->'moon'->>'longitude' AS moon_longitude,
       moon_nakshatra,
       moon_nakshatra_pada
FROM birth_charts
WHERE user_id IN (
    '42527e69-bd1b-4c09-a57c-ef3785f0f7d1'::uuid,
    'e0668425-3ae7-4567-baa1-fb659666622e'::uuid
);
