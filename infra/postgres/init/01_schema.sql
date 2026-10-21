CREATE TABLE users (
    user_id     BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    email       TEXT NOT NULL UNIQUE,
    full_name   TEXT NOT NULL,
    country     TEXT,
    plan        TEXT NOT NULL DEFAULT 'free'
                CHECK (plan IN ('free', 'pro', 'team')),
    created_at  TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at  TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE repos (
    repo_id           BIGINT PRIMARY KEY,   -- GitHub's own repository id
    full_name         TEXT NOT NULL UNIQUE, -- e.g. owner/name
    primary_language  TEXT,
    created_at        TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at        TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE watchlist_items (
    user_id   BIGINT NOT NULL REFERENCES users (user_id) ON DELETE CASCADE,
    repo_id   BIGINT NOT NULL REFERENCES repos (repo_id),
    added_at  TIMESTAMPTZ NOT NULL DEFAULT now(),
    PRIMARY KEY (user_id, repo_id)
);

CREATE TABLE alert_rules (
    rule_id     BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    user_id     BIGINT NOT NULL REFERENCES users (user_id) ON DELETE CASCADE,
    repo_id     BIGINT NOT NULL REFERENCES repos (repo_id),
    metric      TEXT NOT NULL
                CHECK (metric IN ('stars_per_hour', 'open_issues', 'first_response_hours')),
    threshold   NUMERIC NOT NULL,
    is_active   BOOLEAN NOT NULL DEFAULT true,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at  TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_alert_rules_user ON alert_rules (user_id);
CREATE INDEX idx_watchlist_repo ON watchlist_items (repo_id);

CREATE OR REPLACE FUNCTION set_updated_at() RETURNS trigger AS $$
BEGIN
    NEW.updated_at = now();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_users_updated BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION set_updated_at();
CREATE TRIGGER trg_repos_updated BEFORE UPDATE ON repos
    FOR EACH ROW EXECUTE FUNCTION set_updated_at();
CREATE TRIGGER trg_alert_rules_updated BEFORE UPDATE ON alert_rules
    FOR EACH ROW EXECUTE FUNCTION set_updated_at();