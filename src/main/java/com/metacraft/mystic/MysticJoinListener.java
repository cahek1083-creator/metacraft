package com.metacraft.mystic;

import org.bukkit.event.EventHandler;
import org.bukkit.event.Listener;
import org.bukkit.event.player.PlayerJoinEvent;

public class MysticJoinListener implements Listener {

    private final MysticEntityPlugin plugin;
    private final MysticManager manager;

    public MysticJoinListener(MysticEntityPlugin plugin, MysticManager manager) {
        this.plugin = plugin;
        this.manager = manager;
    }

    @EventHandler
    public void onJoin(PlayerJoinEvent event) {
        if (!manager.isActive()) {
            return;
        }

        String prefix = plugin.getConfig().getString("messages.prefix", "");
        event.getPlayer().sendMessage(manager.colorize(prefix + "&8Ты чувствуешь, что за тобой наблюдают..."));
    }
}
