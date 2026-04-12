package com.metacraft.mystic;

import org.bukkit.ChatColor;

import java.util.Arrays;
import java.util.Optional;

public enum MysticEntityType {
    HEROBRINE("&fHerobrine", ChatColor.WHITE),
    LUCAS("&cLucas", ChatColor.RED),
    ERROR303("&bError303", ChatColor.AQUA),
    NULL("&8Null", ChatColor.DARK_GRAY);

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
