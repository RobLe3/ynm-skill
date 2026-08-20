# Architecture

All persistence calls pass through `AccountService`. UI components must not access the database adapter directly.
