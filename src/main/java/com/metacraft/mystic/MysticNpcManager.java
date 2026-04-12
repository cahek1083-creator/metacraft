package com.metacraft.mystic;

import org.bukkit.Bukkit;
import org.bukkit.Location;
import org.bukkit.NamespacedKey;
import org.bukkit.World;
import org.bukkit.entity.Entity;
import org.bukkit.entity.EntityType;
import org.bukkit.entity.LivingEntity;
import org.bukkit.entity.Mob;
import org.bukkit.persistence.PersistentDataContainer;
import org.bukkit.persistence.PersistentDataType;

import java.util.HashSet;
import java.util.Set;
import java.util.UUID;

public class MysticNpcManager {

    private final MysticEntityPlugin plugin;
    private final NamespacedKey npcKey;
    private final Set<UUID> trackedNpcs = new HashSet<>();

    public MysticNpcManager(MysticEntityPlugin plugin) {
        this.plugin = plugin;
        this.npcKey = new NamespacedKey(plugin, "mystic_npc");
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

    private void setupNpc(MysticEntityType type, LivingEntity entity) {
        entity.setCustomName(type.getDisplayName());
        entity.setCustomNameVisible(true);
        entity.setAI(false);
        entity.setSilent(true);
        entity.setInvulnerable(true);
        entity.setCollidable(false);
        entity.setGlowing(false);
        entity.setGravity(false);

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
        PersistentDataContainer container = entity.getPersistentDataContainer();
        return container.has(npcKey, PersistentDataType.STRING);
    }
}
