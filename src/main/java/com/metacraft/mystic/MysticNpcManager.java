package com.metacraft.mystic;

import org.bukkit.Bukkit;
import org.bukkit.Color;
import org.bukkit.Location;
import org.bukkit.NamespacedKey;
import org.bukkit.Particle;
import org.bukkit.World;
import org.bukkit.entity.Entity;
import org.bukkit.entity.EntityType;
import org.bukkit.entity.LivingEntity;
import org.bukkit.entity.Mob;
import org.bukkit.persistence.PersistentDataContainer;
import org.bukkit.persistence.PersistentDataType;
import org.bukkit.scheduler.BukkitTask;

import java.util.HashSet;
import java.util.Set;
import java.util.UUID;

public class MysticNpcManager {

    private final MysticEntityPlugin plugin;
    private final NamespacedKey npcKey;
    private final Set<UUID> trackedNpcs = new HashSet<>();
    private BukkitTask auraTask;

    public MysticNpcManager(MysticEntityPlugin plugin) {
        this.plugin = plugin;
        this.npcKey = new NamespacedKey(plugin, "mystic_npc");
        startAuraTask();
    }

    public LivingEntity spawnNpc(MysticEntityType type, Location location, boolean temporary, long lifetimeTicks) {
        World world = location.getWorld();
        if (world == null) {
            return null;
        }

        EntityType entityType = toEntityType(type);
        Entity entity = world.spawnEntity(location, entityType);
        if (!(entity instanceof LivingEntity living)) {
            entity.remove();
            return null;
        }

        setupNpc(type, living);
        trackedNpcs.add(living.getUniqueId());

        if (temporary) {
            Bukkit.getScheduler().runTaskLater(plugin, () -> {
                if (living.isValid()) {
                    trackedNpcs.remove(living.getUniqueId());
                    living.remove();
                }
            }, lifetimeTicks);
        }

        return living;
    }

    public int clearAllNpcs() {
        int removed = 0;
        for (World world : Bukkit.getWorlds()) {
            for (LivingEntity living : world.getLivingEntities()) {
                if (isMysticNpc(living)) {
                    living.remove();
                    removed++;
                }
            }
        }
        trackedNpcs.clear();
        return removed;
    }

    public void shutdown() {
        if (auraTask != null) {
            auraTask.cancel();
            auraTask = null;
        }
        clearAllNpcs();
    }

    private void startAuraTask() {
        auraTask = Bukkit.getScheduler().runTaskTimer(plugin, () -> {
            for (World world : Bukkit.getWorlds()) {
                for (LivingEntity living : world.getLivingEntities()) {
                    MysticEntityType type = getNpcType(living);
                    if (type == null) {
                        continue;
                    }
                    spawnAura(living, type);
                }
            }
        }, 20L, 40L);
    }

    private void spawnAura(LivingEntity entity, MysticEntityType type) {
        Location loc = entity.getLocation().add(0, 1.1, 0);
        entity.getWorld().spawnParticle(Particle.SOUL, loc, 8, 0.35, 0.35, 0.35, 0.01);
        entity.getWorld().spawnParticle(Particle.SMOKE_NORMAL, loc, 6, 0.4, 0.4, 0.4, 0.01);

        Color color = switch (type) {
            case HEROBRINE -> Color.WHITE;
            case LUCAS -> Color.RED;
            case ERROR303 -> Color.AQUA;
            case NULL -> Color.fromRGB(40, 40, 40);
        };

        Particle.DustOptions dust = new Particle.DustOptions(color, 1.1f);
        entity.getWorld().spawnParticle(Particle.REDSTONE, loc, 12, 0.45, 0.6, 0.45, 0.01, dust);
    }

    private void setupNpc(MysticEntityType type, LivingEntity entity) {
        entity.setCustomName(type.getDisplayName());
        entity.setCustomNameVisible(true);
        entity.setAI(false);
        entity.setSilent(true);
        entity.setInvulnerable(true);
        entity.setCollidable(false);
        entity.setGlowing(true);
        entity.setGravity(true);
        entity.setRemoveWhenFarAway(false);

        if (entity instanceof Mob mob) {
            mob.setAware(false);
            mob.setCanPickupItems(false);
        }

        PersistentDataContainer container = entity.getPersistentDataContainer();
        container.set(npcKey, PersistentDataType.STRING, type.name());
    }

    private EntityType toEntityType(MysticEntityType type) {
        return switch (type) {
            case HEROBRINE -> EntityType.ZOMBIE;
            case LUCAS -> EntityType.VINDICATOR;
            case ERROR303 -> EntityType.WITHER_SKELETON;
            case NULL -> EntityType.ENDERMAN;
        };
    }

    private boolean isMysticNpc(LivingEntity entity) {
        return getNpcType(entity) != null;
    }

    private MysticEntityType getNpcType(LivingEntity entity) {
        PersistentDataContainer container = entity.getPersistentDataContainer();
        String raw = container.get(npcKey, PersistentDataType.STRING);
        if (raw == null) {
            return null;
        }
        return MysticEntityType.fromInput(raw).orElse(null);
    }
}
