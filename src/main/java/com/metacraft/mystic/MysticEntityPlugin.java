package com.metacraft.mystic;

import org.bukkit.Bukkit;
import org.bukkit.plugin.java.JavaPlugin;

public class MysticEntityPlugin extends JavaPlugin {

    private MysticManager mysticManager;

    @Override
    public void onEnable() {
        saveDefaultConfig();

        this.mysticManager = new MysticManager(this);

        MysticCommand mysticCommand = new MysticCommand(this, mysticManager);
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
