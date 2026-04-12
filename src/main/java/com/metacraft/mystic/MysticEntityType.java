package com.metacraft.mystic;

import org.bukkit.ChatColor;

import java.util.Arrays;
import java.util.Optional;

public enum MysticEntityType {
    HEROBRINE("&fHerobrine", ChatColor.WHITE),
    LUCAS("&fLucas", ChatColor.WHITE),
    ERROR303("&fError303", ChatColor.WHITE),
    NULL("&fNull", ChatColor.WHITE);

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
