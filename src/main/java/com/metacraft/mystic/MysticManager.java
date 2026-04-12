package com.metacraft.mystic;

import org.bukkit.Bukkit;
import org.bukkit.ChatColor;
import org.bukkit.GameMode;
import org.bukkit.Location;
import org.bukkit.Particle;
import org.bukkit.Sound;
import org.bukkit.World;
import org.bukkit.entity.Player;
import org.bukkit.potion.PotionEffect;
import org.bukkit.potion.PotionEffectType;
import org.bukkit.scheduler.BukkitTask;

import java.util.ArrayList;
import java.util.List;
import java.util.concurrent.ThreadLocalRandom;

public class MysticManager {

    private final MysticEntityPlugin plugin;
    private final MysticNpcManager npcManager;
    private final ThreadLocalRandom random = ThreadLocalRandom.current();
    private BukkitTask pulseTask;
    private boolean active;
    private boolean bergMode;

    public MysticManager(MysticEntityPlugin plugin, MysticNpcManager npcManager) {
        this.plugin = plugin;
        this.npcManager = npcManager;
        this.bergMode = plugin.getConfig().getBoolean("berg-mode-enabled", true);
    }

    public boolean isActive() {
        return active;
    }

    public boolean isBergMode() {
        return bergMode;
    }

    public void setBergMode(boolean enabled) {
        this.bergMode = enabled;
        String prefix = plugin.getConfig().getString("messages.prefix", "");
        String state = enabled ? "&aBerg-режим включен." : "&cBerg-режим выключен.";
        Bukkit.broadcastMessage(colorize(prefix + state));
    }

    public void start() {
        if (active) {
            return;
        }
        active = true;

        int interval = Math.max(100, plugin.getConfig().getInt("pulse-interval-ticks", 1200));
        pulseTask = Bukkit.getScheduler().runTaskTimer(plugin, this::runRandomPulse, 100L, interval);
        broadcastConfigured("messages.enabled");
    }

    public void stop() {
        active = false;
        if (pulseTask != null) {
            pulseTask.cancel();
            pulseTask = null;
        }
        npcManager.shutdown();
        broadcastConfigured("messages.disabled");
    }

    public void runManualPulse(MysticEntityType forcedType) {
        if (!active) {
            return;
        }
        if (forcedType == null) {
            runRandomPulse();
            return;
        }
        performManifestation(forcedType);
    }

    private void runRandomPulse() {
        if (!active) {
            return;
        }

        List<MysticEntityType> configured = getConfiguredEntities();
        if (configured.isEmpty()) {
            configured.add(MysticEntityType.HEROBRINE);
        }

        MysticEntityType selected = configured.get(random.nextInt(configured.size()));
        Bukkit.broadcastMessage(colorize(plugin.getConfig().getString("messages.prefix", "")
                + plugin.getConfig().getString("messages.pulse", "")));
        performManifestation(selected);
    }

    private void performManifestation(MysticEntityType type) {
        for (Player player : Bukkit.getOnlinePlayers()) {
            if (player.getGameMode() == GameMode.SPECTATOR) {
                continue;
            }

            Location around = randomNearby(player.getLocation());
            player.spawnParticle(Particle.SMOKE_NORMAL, around, 25, 0.4, 0.8, 0.4, 0.01);
            player.spawnParticle(Particle.SOUL, around, 10, 0.3, 0.7, 0.3, 0.01);
            player.playSound(player.getLocation(), Sound.AMBIENT_SOUL_SAND_VALLEY_MOOD, 0.8f, 0.5f);

            long npcLifetime = Math.max(200L, plugin.getConfig().getLong("npc-lifetime-ticks", 1200L));
            npcManager.spawnNpc(type, around, true, npcLifetime);

            String line = plugin.getConfig().getString("messages.prefix", "")
                    + type.getColor()
                    + "Сущность замечена рядом: " + type.getDisplayName();
            player.sendMessage(colorize(line));

            String pluginHint = plugin.getConfig().getString("messages.npc-spawn", "&d[МИСТИКА] Явление типа %entity% материализовано.")
                    .replace("%entity%", type.name());
            player.sendMessage(colorize(plugin.getConfig().getString("messages.prefix", "") + pluginHint));

            if (bergMode) {
                runBergStyleEffects(player, type, around);
            }

            if (random.nextDouble() < 0.25) {
                player.playSound(player.getLocation(), Sound.ENTITY_ENDERMAN_STARE, 0.8f, 0.7f);
            }
        }

        if (bergMode) {
            fakeServerAnomaly(type);
        }
    }

    private void runBergStyleEffects(Player player, MysticEntityType type, Location around) {
        player.sendTitle(colorize("&f" + type.name()), colorize("&7наблюдает за тобой"), 10, 40, 10);
        player.addPotionEffect(new PotionEffect(PotionEffectType.DARKNESS, 50, 0, false, false, false));
        player.addPotionEffect(new PotionEffect(PotionEffectType.SLOW, 30, 1, false, false, false));
        player.playSound(player.getLocation(), Sound.ENTITY_WARDEN_NEARBY_CLOSE, 0.8f, 0.8f);
        player.getWorld().strikeLightningEffect(around);
        player.getWorld().spawnParticle(Particle.REVERSE_PORTAL, around, 30, 0.4, 1.0, 0.4, 0.02);
    }

    private void fakeServerAnomaly(MysticEntityType type) {
        String name = type.name().toLowerCase();
        String join = ChatColor.YELLOW + name + " joined the game";
        String leave = ChatColor.YELLOW + name + " left the game";
        Bukkit.broadcastMessage(join);

        List<String> lines = plugin.getConfig().getStringList("berg-fake-chat-lines");
        if (!lines.isEmpty()) {
            String selected = lines.get(random.nextInt(lines.size())).replace("%entity%", name);
            Bukkit.broadcastMessage(colorize(selected));
        }

        Bukkit.getScheduler().runTaskLater(plugin, () -> Bukkit.broadcastMessage(leave), 40L);
    }

    private Location randomNearby(Location origin) {
        World world = origin.getWorld();
        if (world == null) {
            return origin;
        }

        double dx = random.nextDouble(-5, 6);
        double dz = random.nextDouble(-5, 6);
        int x = (int) Math.floor(origin.getX() + dx);
        int z = (int) Math.floor(origin.getZ() + dz);
        int y = world.getHighestBlockYAt(x, z);
        return new Location(world, x + 0.5, y + 1.1, z + 0.5);
    }

    private List<MysticEntityType> getConfiguredEntities() {
        List<String> raw = plugin.getConfig().getStringList("entities");
        List<MysticEntityType> result = new ArrayList<>();
        for (String line : raw) {
            MysticEntityType.fromInput(line).ifPresent(result::add);
        }
        return result;
    }

    public void broadcastConfigured(String key) {
        String prefix = plugin.getConfig().getString("messages.prefix", "");
        String message = plugin.getConfig().getString(key, "");
        Bukkit.broadcastMessage(colorize(prefix + message));
    }

    public String colorize(String text) {
        return ChatColor.translateAlternateColorCodes('&', text);
    }
}
