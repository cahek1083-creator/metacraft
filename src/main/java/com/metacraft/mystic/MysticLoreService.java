package com.metacraft.mystic;

import java.util.EnumMap;
import java.util.Map;

public class MysticLoreService {

    private final Map<MysticEntityType, MythEntry> lore = new EnumMap<>(MysticEntityType.class);

    public MysticLoreService() {
        lore.put(MysticEntityType.HEROBRINE, new MythEntry(
                "Herobrine",
                "Одна из самых известных легенд Minecraft: таинственный персонаж со светящимися глазами, которого игроки якобы видели в мире. В официальных патчноутах Mojang долгое время шутили фразой 'Removed Herobrine'.",
                "https://minecraft.wiki/w/Herobrine"
        ));

        lore.put(MysticEntityType.ERROR303, new MythEntry(
                "Entity 303",
                "Фанатская крипипаста о 'взломанной сущности' и саботаже миров/серверов. В каноне Minecraft этой сущности нет, но она популярна в хоррор-историях сообщества.",
                "https://minecraftcreepypasta.fandom.com/wiki/Entity_303"
        ));

        lore.put(MysticEntityType.NULL, new MythEntry(
                "Null",
                "Ещё одна фанатская легенда: тёмная аномалия/наблюдатель, которая появляется рядом с игроком и оставляет странные следы. Также не является официальной сущностью Mojang.",
                "https://minecraftcreepypasta.fandom.com/wiki/Null"
        ));

        lore.put(MysticEntityType.LUCAS, new MythEntry(
                "Lucas",
                "Современная пользовательская хоррор-легенда/мод-сущность, распространяемая в модах и роликах сообщества. Чаще фигурирует как враждебный преследователь.",
                "https://www.curseforge.com/minecraft/mc-mods/lucas-horror"
        ));
    }

    public MythEntry get(MysticEntityType type) {
        return lore.get(type);
    }
}
