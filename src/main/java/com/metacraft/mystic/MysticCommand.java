package com.metacraft.mystic;

import org.bukkit.command.Command;
import org.bukkit.command.CommandExecutor;
import org.bukkit.command.CommandSender;
import org.bukkit.command.TabCompleter;

import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;
import java.util.Locale;
import java.util.stream.Collectors;

public class MysticCommand implements CommandExecutor, TabCompleter {

    private final MysticEntityPlugin plugin;
    private final MysticManager manager;

    public MysticCommand(MysticEntityPlugin plugin, MysticManager manager) {
        this.plugin = plugin;
        this.manager = manager;
    }

    @Override
    public boolean onCommand(CommandSender sender, Command command, String label, String[] args) {
        if (args.length == 0) {
            sender.sendMessage("§7Использование: /mystic <start|stop|pulse|status>");
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
            case "pulse" -> {
                if (!manager.isActive()) {
                    sender.sendMessage("§cСначала включите режим: /mystic start");
                    return true;
                }

                if (args.length == 1) {
                    manager.runManualPulse(null);
                    sender.sendMessage("§dСлучайный мистический импульс запущен.");
                    return true;
                }

                MysticEntityType.fromInput(args[1]).ifPresentOrElse(type -> {
                    manager.runManualPulse(type);
                    sender.sendMessage("§dИмпульс сущности запущен: " + type.getDisplayName());
                }, () -> {
                    String msg = plugin.getConfig().getString("messages.unknown-entity", "Неизвестная сущность: %entity%")
                            .replace("%entity%", args[1]);
                    sender.sendMessage(manager.colorize(msg));
                });
            }
            default -> sender.sendMessage("§cНеизвестная команда. Используйте /mystic status");
        }

        return true;
    }

    @Override
    public List<String> onTabComplete(CommandSender sender, Command command, String alias, String[] args) {
        if (args.length == 1) {
            return filter(Arrays.asList("start", "stop", "pulse", "status"), args[0]);
        }

        if (args.length == 2 && args[0].equalsIgnoreCase("pulse")) {
            List<String> entities = Arrays.stream(MysticEntityType.values())
                    .map(Enum::name)
                    .map(String::toLowerCase)
                    .collect(Collectors.toList());
            return filter(entities, args[1]);
        }

        return List.of();
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
