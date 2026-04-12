package com.metacraft.mystic;

import org.bukkit.Bukkit;
import org.bukkit.plugin.java.JavaPlugin;

public class MysticEntityPlugin extends JavaPlugin {

    private MysticManager mysticManager;

    @Override
    public void onEnable() {
        saveDefaultConfig();

        MysticLoreService loreService = new MysticLoreService();
        MysticNpcManager npcManager = new MysticNpcManager(this);
        this.mysticManager = new MysticManager(this, npcManager);

        MysticCommand mysticCommand = new MysticCommand(this, mysticManager, npcManager, loreService);
        if (getCommand("mystic") != null) {
            getCommand("mystic").setExecutor(mysticCommand);
            getCommand("mystic").setTabCompleter(mysticCommand);
        }

        Bukkit.getPluginManager().registerEvents(new MysticJoinListener(this, mysticManager), this);

        if (getConfig().getBoolean("enabled-by-default", false)) {
            mysticManager.start();
        }

        getLogger().info("MysticEntityPlugin enabled.");
    }

    @Override
    public void onDisable() {
        if (mysticManager != null) {
            mysticManager.stop();
        }
        getLogger().info("MysticEntityPlugin disabled.");
    }
}
