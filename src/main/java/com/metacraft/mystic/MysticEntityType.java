package com.metacraft.mystic;

import org.bukkit.ChatColor;

import java.util.Arrays;
import java.util.Optional;

public enum MysticEntityType {
    HEROBRINE("&0Herobrine", ChatColor.BLACK),
    LUCAS("&0Lucas", ChatColor.BLACK),
    ERROR303("&0Error303", ChatColor.BLACK),
    NULL("&0Null", ChatColor.BLACK);

    private final String displayName;
    private final ChatColor color;

    MysticEntityType(String displayName, ChatColor color) {
        this.displayName = displayName;
        this.color = color;
    }

    public String getDisplayName() {
        return ChatColor.translateAlternateColorCodes('&', displayName);
    }

    public ChatColor getColor() {
        return color;
    }

    public static Optional<MysticEntityType> fromInput(String input) {
        return Arrays.stream(values())
                .filter(type -> type.name().equalsIgnoreCase(input))
                .findFirst();
    }
}
