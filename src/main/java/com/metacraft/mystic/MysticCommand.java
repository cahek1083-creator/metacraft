package com.metacraft.mystic;

import org.bukkit.Location;
import org.bukkit.command.Command;
import org.bukkit.command.CommandExecutor;
import org.bukkit.command.CommandSender;
import org.bukkit.command.TabCompleter;
import org.bukkit.entity.Player;

import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;
import java.util.Locale;
import java.util.stream.Collectors;

public class MysticCommand implements CommandExecutor, TabCompleter {

    private final MysticEntityPlugin plugin;
    private final MysticManager manager;
    private final MysticNpcManager npcManager;
    private final MysticLoreService loreService;

    public MysticCommand(MysticEntityPlugin plugin, MysticManager manager, MysticNpcManager npcManager, MysticLoreService loreService) {
        this.plugin = plugin;
        this.manager = manager;
        this.npcManager = npcManager;
        this.loreService = loreService;
    }

    @Override
    public boolean onCommand(CommandSender sender, Command command, String label, String[] args) {
        if (args.length == 0) {
            sender.sendMessage("§7Использование: /mystic <start|stop|pulse|status|npc|lore>");
            return true;
        }

        String sub = args[0].toLowerCase(Locale.ROOT);
        switch (sub) {
            case "start" -> {
                manager.start();
                sender.sendMessage("§aМистический режим включен.");
            }
            case "stop" -> {
                manager.stop();
                sender.sendMessage("§cМистический режим выключен.");
            }
            case "status" -> sender.sendMessage(manager.isActive() ? "§aАктивен" : "§cНеактивен");
            case "pulse" -> handlePulse(sender, args);
            case "npc" -> handleNpc(sender, args);
            case "lore" -> handleLore(sender, args);
            default -> sender.sendMessage("§cНеизвестная команда. Используйте /mystic status");
        }

        return true;
    }

    private void handlePulse(CommandSender sender, String[] args) {
        if (!manager.isActive()) {
            sender.sendMessage("§cСначала включите режим: /mystic start");
            return;
        }

        if (args.length == 1) {
            manager.runManualPulse(null);
            sender.sendMessage("§dСлучайный мистический импульс запущен.");
            return;
        }

        MysticEntityType.fromInput(args[1]).ifPresentOrElse(type -> {
            manager.runManualPulse(type);
            sender.sendMessage("§dИмпульс сущности запущен: " + type.getDisplayName());
        }, () -> sender.sendMessage(unknownEntity(args[1])));
    }

    private void handleNpc(CommandSender sender, String[] args) {
        if (args.length < 2) {
            sender.sendMessage("§7Использование: /mystic npc <spawn|clear>");
            return;
        }

        if (args[1].equalsIgnoreCase("clear")) {
            int removed = npcManager.clearAllNpcs();
            sender.sendMessage("§aУдалено мистических NPC: §f" + removed);
            return;
        }

        if (!args[1].equalsIgnoreCase("spawn")) {
            sender.sendMessage("§cДоступно: /mystic npc spawn <entity> [count]");
            return;
        }

        if (!(sender instanceof Player player)) {
            sender.sendMessage("§cSpawn NPC доступен только игроку в мире.");
            return;
        }

        if (args.length < 3) {
            sender.sendMessage("§cУкажи сущность: herobrine/lucas/error303/null");
            return;
        }

        MysticEntityType.fromInput(args[2]).ifPresentOrElse(type -> {
            int count = 1;
            if (args.length >= 4) {
                try {
                    count = Math.max(1, Math.min(10, Integer.parseInt(args[3])));
                } catch (NumberFormatException ignored) {
                    sender.sendMessage("§eКоличество должно быть числом, использую 1.");
                }
            }

            for (int i = 0; i < count; i++) {
                Location loc = player.getLocation().clone().add((i % 3) - 1, 0, (i / 3) + 2);
                npcManager.spawnNpc(type, loc, false, 0L);
            }
            sender.sendMessage("§aЗаспавнено NPC: §f" + count + " §7тип: " + type.getDisplayName());
        }, () -> sender.sendMessage(unknownEntity(args[2])));
    }

    private void handleLore(CommandSender sender, String[] args) {
        if (args.length < 2) {
            sender.sendMessage("§7Использование: /mystic lore <entity>");
            return;
        }

        MysticEntityType.fromInput(args[1]).ifPresentOrElse(type -> {
            MythEntry entry = loreService.get(type);
            if (entry == null) {
                sender.sendMessage("§cДля этой сущности нет описания.");
                return;
            }
            sender.sendMessage("§5" + entry.title());
            sender.sendMessage("§7" + entry.summary());
            sender.sendMessage("§8Источник: §b" + entry.sourceUrl());
        }, () -> sender.sendMessage(unknownEntity(args[1])));
    }

    private String unknownEntity(String arg) {
        String msg = plugin.getConfig().getString("messages.unknown-entity", "Неизвестная сущность: %entity%")
                .replace("%entity%", arg);
        return manager.colorize(msg);
    }

    @Override
    public List<String> onTabComplete(CommandSender sender, Command command, String alias, String[] args) {
        if (args.length == 1) {
            return filter(Arrays.asList("start", "stop", "pulse", "status", "npc", "lore"), args[0]);
        }

        if (args.length == 2 && args[0].equalsIgnoreCase("pulse")) {
            return filter(entityValues(), args[1]);
        }

        if (args.length == 2 && args[0].equalsIgnoreCase("npc")) {
            return filter(Arrays.asList("spawn", "clear"), args[1]);
        }

        if (args.length == 3 && args[0].equalsIgnoreCase("npc") && args[1].equalsIgnoreCase("spawn")) {
            return filter(entityValues(), args[2]);
        }

        if (args.length == 2 && args[0].equalsIgnoreCase("lore")) {
            return filter(entityValues(), args[1]);
        }

        return List.of();
    }

    private List<String> entityValues() {
        return Arrays.stream(MysticEntityType.values())
                .map(Enum::name)
                .map(String::toLowerCase)
                .collect(Collectors.toList());
    }

    private List<String> filter(List<String> source, String token) {
        String lower = token.toLowerCase(Locale.ROOT);
        List<String> result = new ArrayList<>();
        for (String entry : source) {
            if (entry.startsWith(lower)) {
                result.add(entry);
            }
        }
        return result;
    }
}
