import Py4GW
from Py4GWCoreLib import GLOBAL_CACHE, SpiritModelID, ThrottledTimer, Routines, Range, Allegiance, AgentArray
from Py4GWCoreLib import Weapon
from Py4GWCoreLib.enums import SPIRIT_BUFF_MAP
from .custom_skill import CustomSkillClass
from .targeting import TargetLowestAlly, TargetLowestAllyEnergy, TargetClusteredEnemy, TargetLowestAllyCaster, TargetLowestAllyMartial, TargetLowestAllyMelee, TargetLowestAllyRanged, GetAllAlliesArray
from .targeting import GetEnemyAttacking, GetEnemyCasting, GetEnemyCastingSpell, GetEnemyInjured, GetEnemyConditioned
from .targeting import GetEnemyHexed, GetEnemyDegenHexed, GetEnemyEnchanted, GetEnemyMoving, GetEnemyKnockedDown
from .targeting import GetEnemyBleeding, GetEnemyPoisoned, GetEnemyCrippled
from .types import SkillNature, Skilltarget, SkillType
from .constants import MAX_NUM_PLAYERS
from typing import Optional

class UniqueSkills:
    def __init__(self):
        self.energy_drain = GLOBAL_CACHE.Skill.GetID("Energy_Drain") 
        self.energy_tap = GLOBAL_CACHE.Skill.GetID("Energy_Tap")
        self.ether_lord = GLOBAL_CACHE.Skill.GetID("Ether_Lord")
        self.essence_strike = GLOBAL_CACHE.Skill.GetID("Essence_Strike")
        self.glowing_signet = GLOBAL_CACHE.Skill.GetID("Glowing_Signet")
        self.clamor_of_souls = GLOBAL_CACHE.Skill.GetID("Clamor_of_Souls")
        self.waste_not_want_not = GLOBAL_CACHE.Skill.GetID("Waste_Not_Want_Not")
        self.mend_body_and_soul = GLOBAL_CACHE.Skill.GetID("Mend_Body_and_Soul")
        self.grenths_balance = GLOBAL_CACHE.Skill.GetID("Grenths_Balance")
        self.deaths_retreat = GLOBAL_CACHE.Skill.GetID("Deaths_Retreat")
        self.plague_sending = GLOBAL_CACHE.Skill.GetID("Plague_Sending")
        self.plague_signet = GLOBAL_CACHE.Skill.GetID("Plague_Signet")
        self.plague_touch = GLOBAL_CACHE.Skill.GetID("Plague_Touch")
        self.golden_fang_strike = GLOBAL_CACHE.Skill.GetID("Golden_Fang_Strike")
        self.golden_fox_strike = GLOBAL_CACHE.Skill.GetID("Golden_Fox_Strike")
        self.golden_lotus_strike = GLOBAL_CACHE.Skill.GetID("Golden_Lotus_Strike")
        self.golden_phoenix_strike = GLOBAL_CACHE.Skill.GetID("Golden_Phoenix_Strike")
        self.golden_skull_strike = GLOBAL_CACHE.Skill.GetID("Golden_Skull_Strike")
        self.brutal_weapon = GLOBAL_CACHE.Skill.GetID("Brutal_Weapon")
        self.signet_of_removal = GLOBAL_CACHE.Skill.GetID("Signet_of_Removal")
        self.dwaynas_kiss = GLOBAL_CACHE.Skill.GetID("Dwaynas_Kiss")
        self.unnatural_signet = GLOBAL_CACHE.Skill.GetID("Unnatural_Signet")
        self.toxic_chill = GLOBAL_CACHE.Skill.GetID("Toxic_Chill")
        self.discord = GLOBAL_CACHE.Skill.GetID("Discord")
        self.empathic_removal = GLOBAL_CACHE.Skill.GetID("Empathic_Removal")
        self.iron_palm = GLOBAL_CACHE.Skill.GetID("Iron_Palm")
        self.melandrus_resilience = GLOBAL_CACHE.Skill.GetID("Melandrus_Resilience")
        self.necrosis = GLOBAL_CACHE.Skill.GetID("Necrosis")
        self.peace_and_harmony = GLOBAL_CACHE.Skill.GetID("Peace_and_Harmony")
        self.purge_signet = GLOBAL_CACHE.Skill.GetID("Purge_Signet")
        self.resilient_weapon = GLOBAL_CACHE.Skill.GetID("Resilient_Weapon")
        self.gaze_from_beyond = GLOBAL_CACHE.Skill.GetID("Gaze_from_Beyond")
        self.spirit_burn = GLOBAL_CACHE.Skill.GetID("Spirit_Burn")
        self.signet_of_ghostly_might = GLOBAL_CACHE.Skill.GetID("Signet_of_Ghostly_Might")
        self.burning = GLOBAL_CACHE.Skill.GetID("Burning")
        self.blind = GLOBAL_CACHE.Skill.GetID("Blind")
        self.cracked_armor = GLOBAL_CACHE.Skill.GetID("Cracked_Armor")
        self.crippled = GLOBAL_CACHE.Skill.GetID("Crippled")
        self.dazed = GLOBAL_CACHE.Skill.GetID("Dazed")
        self.deep_wound = GLOBAL_CACHE.Skill.GetID("Deep_Wound")
        self.disease = GLOBAL_CACHE.Skill.GetID("Disease")
        self.poison = GLOBAL_CACHE.Skill.GetID("Poison")
        self.weakness = GLOBAL_CACHE.Skill.GetID("Weakness")
        self.comfort_animal = GLOBAL_CACHE.Skill.GetID("Comfort_Animal")
        self.heal_as_one = GLOBAL_CACHE.Skill.GetID("Heal_as_One")
        self.heroic_refrain = GLOBAL_CACHE.Skill.GetID("Heroic_Refrain")
        self.natures_blessing = GLOBAL_CACHE.Skill.GetID("Natures_Blessing")
        self.relentless_assault = GLOBAL_CACHE.Skill.GetID("Relentless_Assault")

MAX_SKILLS = 8
custom_skill_data_handler = CustomSkillClass()

def _PrioritizeSkills(Skill_Data, Skill_Order):
        """
        Create a priority-based skill execution order.
        """
        #initialize skillbar
        original_skills = []
        for i in range(MAX_SKILLS):
            original_skills.append(Skill_Data(i+1))

        # Initialize the pointer and tracking list
        ptr = 0
        ptr_chk = [False] * MAX_SKILLS
        ordered_skills = []
        
        priorities = [
            SkillNature.CustomA,
            SkillNature.Interrupt,
            SkillNature.CustomB,
            SkillNature.Enchantment_Removal,
            SkillNature.CustomC,
            SkillNature.Healing,
            SkillNature.CustomD,
            SkillNature.Resurrection,
            SkillNature.CustomE,
            SkillNature.Hex_Removal,
            SkillNature.CustomF,
            SkillNature.Condi_Cleanse,
            SkillNature.CustomG,
            SkillNature.SelfTargeted,
            SkillNature.CustomH,
            SkillNature.EnergyBuff,
            SkillNature.CustomI,
            SkillNature.Buff,
            SkillNature.CustomJ,
            SkillNature.OffensiveA,
            SkillNature.CustomK,
            SkillNature.OffensiveB,
            SkillNature.CustomL,
            SkillNature.OffensiveC,
            SkillNature.CustomM,
            SkillNature.Offensive,
            SkillNature.CustomN,
        ]

        for priority in priorities:
            #for i in range(ptr,MAX_SKILLS):
            for i in range(MAX_SKILLS):
                skill = original_skills[i]
                if not ptr_chk[i] and skill.custom_skill_data.Nature == priority.value:
                    Skill_Order[ptr] = i
                    ptr_chk[i] = True
                    ptr += 1
                    ordered_skills.append(skill)
        
        skill_types = [
            SkillType.Form,
            SkillType.Enchantment,
            SkillType.EchoRefrain,
            SkillType.WeaponSpell,
            SkillType.Chant,
            SkillType.Preparation,
            SkillType.Ritual,
            SkillType.Ward,
            SkillType.Well,
            SkillType.Stance,
            SkillType.Shout,
            SkillType.Glyph,
            SkillType.Signet,
            SkillType.Hex,
            SkillType.Trap,
            SkillType.Spell,
            SkillType.Skill,
            SkillType.PetAttack,
            SkillType.Attack,
        ]

        
        for skill_type in skill_types:
            #for i in range(ptr,MAX_SKILLS):
            for i in range(MAX_SKILLS):
                skill = original_skills[i]
                if not ptr_chk[i] and skill.custom_skill_data.SkillType == skill_type.value:
                    Skill_Order[ptr] = i
                    ptr_chk[i] = True
                    ptr += 1
                    ordered_skills.append(skill)

        combos = [3, 2, 1]  # Dual attack, off-hand attack, lead attack
        for combo in combos:
            #for i in range(ptr,MAX_SKILLS):
            for i in range(MAX_SKILLS):
                skill = original_skills[i]
                if not ptr_chk[i] and GLOBAL_CACHE.Skill.Data.GetCombo(skill.skill_id) == combo:
                    Skill_Order[ptr] = i
                    ptr_chk[i] = True
                    ptr += 1
                    ordered_skills.append(skill)
        
        # Fill in remaining unprioritized skills
        for i in range(MAX_SKILLS):
            if not ptr_chk[i]:
                Skill_Order[ptr] = i
                ptr_chk[i] = True
                ptr += 1
                ordered_skills.append(original_skills[i])
        
        return ordered_skills
    
def _IsSkillReady(slot, skill_order, skills, is_skill_enabled):
        original_index = skill_order[slot]
        if skills[slot].skill_id == 0:
            return False
        if skills[slot].skillbar_data.recharge != 0:
            return False
        return is_skill_enabled[original_index]

def _InCastingRoutine(aftercast_timer, in_casting_routine):
        if aftercast_timer.IsExpired():
                in_casting_routine = False
                aftercast_timer.Reset()

        return in_casting_routine
    
def _GetPartyTarget():
    party_target = Routines.Party.GetPartyTargetID()
    if party_target != 0:
        current_target = GLOBAL_CACHE.Player.GetTargetID()
        if current_target != party_target:
            if GLOBAL_CACHE.Agent.IsLiving(party_target):
                _, alliegeance = GLOBAL_CACHE.Agent.GetAllegiance(party_target)
                if alliegeance != 'Ally' and alliegeance != 'NPC/Minipet':
                    Routines.Targeting.SafeChangeTarget(party_target)
                    return party_target
    return 0

def _GetAppropiateTarget(
    skills,
    unique_skills,
    HasEffect_fn,  # required first
    GetPartytarget_fn,
    multibox: bool = True,
    slot: int = 0,
    is_targeting_enabled: bool = True,
    is_combat_enabled: bool = True,
    combat_distance: float = Range.Earshot.value,
):
        def _TargetClusteredEnemy(combat_distance):
            return TargetClusteredEnemy(combat_distance) if multibox else Routines.Targeting.TargetClusteredEnemy(combat_distance)
        
        def _GetEnemyAttacking(combat_distance):
            return GetEnemyAttacking(combat_distance) if multibox else Routines.Targeting.GetEnemyAttacking(combat_distance)
        
        def _GetEnemyCasting(combat_distance):
            return GetEnemyCasting(combat_distance) if multibox else Routines.Targeting.GetEnemyCasting(combat_distance)
        
        def _GetEnemyCastingSpell(combat_distance):
            return GetEnemyCastingSpell(combat_distance) if multibox else Routines.Targeting.GetEnemyCastingSpell(combat_distance)
        
        def _GetEnemyInjured(combat_distance):
            return GetEnemyInjured(combat_distance) if multibox else Routines.Targeting.GetEnemyInjured(combat_distance)
        
        def _GetEnemyConditioned(combat_distance):
            return GetEnemyConditioned(combat_distance) if multibox else Routines.Targeting.GetEnemyConditioned(combat_distance)
        
        def _GetEnemyBleeding(combat_distance):
            return GetEnemyBleeding(combat_distance) if multibox else Routines.Targeting.GetEnemyBleeding(combat_distance)
        
        def _GetEnemyPoisoned(combat_distance):
            return GetEnemyPoisoned(combat_distance) if multibox else Routines.Targeting.GetEnemyPoisoned(combat_distance)
        
        def _GetEnemyCrippled(combat_distance):
            return GetEnemyCrippled(combat_distance) if multibox else Routines.Targeting.GetEnemyCrippled(combat_distance)
        
        def _GetEnemyHexed(combat_distance):
            return GetEnemyHexed(combat_distance) if multibox else Routines.Targeting.GetEnemyHexed(combat_distance)
        
        def _GetEnemyDegenHexed(combat_distance):
            return GetEnemyDegenHexed(combat_distance) if multibox else Routines.Targeting.GetEnemyDegenHexed(combat_distance)
        
        def _GetEnemyEnchanted(combat_distance):
            return GetEnemyEnchanted(combat_distance) if multibox else Routines.Targeting.GetEnemyEnchanted(combat_distance)
        
        def _GetEnemyMoving(combat_distance):
            return GetEnemyMoving(combat_distance) if multibox else Routines.Targeting.GetEnemyMoving(combat_distance)
        
        def _GetEnemyKnockedDown(combat_distance):
            return GetEnemyKnockedDown(combat_distance) if multibox else Routines.Targeting.GetEnemyKnockedDown(combat_distance)
        
        def _TargetLowestAllyCaster(filter_skill_id=0):
            return TargetLowestAllyCaster(filter_skill_id=filter_skill_id) if multibox else Routines.Targeting.TargetLowestAllyCaster(filter_skill_id=filter_skill_id)
        
        def _TargetLowestAllyMartial(filter_skill_id=0):
            return TargetLowestAllyMartial(filter_skill_id=filter_skill_id) if multibox else Routines.Targeting.TargetLowestAllyMartial(filter_skill_id=filter_skill_id)
        
        def _TargetLowestAllyMelee(filter_skill_id=0):
            return TargetLowestAllyMelee(filter_skill_id=filter_skill_id) if multibox else Routines.Targeting.TargetLowestAllyMelee(filter_skill_id=filter_skill_id)
        
        def _TargetLowestAllyRanged(filter_skill_id=0):
            return TargetLowestAllyRanged(filter_skill_id=filter_skill_id) if multibox else Routines.Targeting.TargetLowestAllyRanged(filter_skill_id=filter_skill_id)
        
        def _TargetLowestAllyEnergy(other_ally=False, filter_skill_id=0):
            return TargetLowestAllyEnergy(other_ally=other_ally, filter_skill_id=filter_skill_id) if multibox else Routines.Targeting.TargetLowestAllyEnergy(other_ally=other_ally, filter_skill_id=filter_skill_id)
        
        def _TargetLowestAlly(other_ally=False, filter_skill_id=0):
            return TargetLowestAlly(other_ally=other_ally, filter_skill_id=filter_skill_id) if multibox else Routines.Targeting.TargetLowestAlly(other_ally=other_ally, filter_skill_id=filter_skill_id)
        
        
        v_target = 0

        if multibox and not is_targeting_enabled:
            return GLOBAL_CACHE.Player.GetTargetID()

        targeting_strict = skills[slot].custom_skill_data.Conditions.TargetingStrict
        target_allegiance =skills[slot].custom_skill_data.TargetAllegiance
        
        
        nearest_enemy = Routines.Agents.GetNearestEnemy(combat_distance)
        lowest_ally = _TargetLowestAlly(skills, slot)

        if skills[slot].skill_id == unique_skills.heroic_refrain:
            if not HasEffect_fn(GLOBAL_CACHE.Player.GetAgentID(), unique_skills.heroic_refrain):
                return GLOBAL_CACHE.Player.GetAgentID()

        if target_allegiance == Skilltarget.Enemy:
            v_target = GetPartytarget_fn()
            if v_target == 0:
                v_target = nearest_enemy
        elif target_allegiance == Skilltarget.EnemyCaster:
            v_target = Routines.Agents.GetNearestEnemyCaster(combat_distance)
            if v_target == 0 and not targeting_strict:
                v_target = nearest_enemy
        elif target_allegiance == Skilltarget.EnemyMartial:
            v_target = Routines.Agents.GetNearestEnemyMartial(combat_distance)
            if v_target == 0 and not targeting_strict:
                v_target = nearest_enemy
        elif target_allegiance == Skilltarget.EnemyMartialMelee:
            v_target = Routines.Agents.GetNearestEnemyMelee(combat_distance)
            if v_target == 0 and not targeting_strict:
                v_target = nearest_enemy
        elif target_allegiance == Skilltarget.EnemyClustered:
            v_target = _TargetClusteredEnemy(combat_distance)
            if v_target == 0 and not targeting_strict:
                v_target = nearest_enemy
        elif target_allegiance == Skilltarget.EnemyAttacking:
            v_target = _GetEnemyAttacking(combat_distance)
            if v_target == 0 and not targeting_strict:
                v_target = nearest_enemy
        elif target_allegiance == Skilltarget.EnemyCasting:
            v_target = _GetEnemyCasting(combat_distance)
            if v_target == 0 and not targeting_strict:
                v_target = nearest_enemy          
        elif target_allegiance == Skilltarget.EnemyCastingSpell:
            v_target = _GetEnemyCastingSpell(combat_distance)
            if v_target == 0 and not targeting_strict:
                v_target = nearest_enemy
        elif target_allegiance == Skilltarget.EnemyInjured:
            v_target = _GetEnemyInjured(combat_distance)
            if v_target == 0 and not targeting_strict:
                v_target = nearest_enemy
        elif target_allegiance == Skilltarget.EnemyConditioned:
            v_target = _GetEnemyConditioned(combat_distance)
            if v_target == 0 and not targeting_strict:
                v_target = nearest_enemy
        elif target_allegiance == Skilltarget.EnemyBleeding:
            v_target = _GetEnemyBleeding(combat_distance)
            if v_target == 0 and not targeting_strict:
                v_target = nearest_enemy
        elif target_allegiance == Skilltarget.EnemyPoisoned:
            v_target = _GetEnemyPoisoned(combat_distance)
            if v_target == 0 and not targeting_strict:
                v_target = nearest_enemy
        elif target_allegiance == Skilltarget.EnemyCrippled:
            v_target = _GetEnemyCrippled(combat_distance)
            if v_target == 0 and not targeting_strict:
                v_target = nearest_enemy
        elif target_allegiance == Skilltarget.EnemyHexed:
            v_target = _GetEnemyHexed(combat_distance)
            if v_target == 0 and not targeting_strict:
                v_target = nearest_enemy
        elif target_allegiance == Skilltarget.EnemyDegenHexed:
            v_target = _GetEnemyDegenHexed(combat_distance)
            if v_target == 0 and not targeting_strict:
                v_target = nearest_enemy
        elif target_allegiance == Skilltarget.EnemyEnchanted:
            v_target = _GetEnemyEnchanted(combat_distance)
            if v_target == 0 and not targeting_strict:
                v_target = nearest_enemy
        elif target_allegiance == Skilltarget.EnemyMoving:
            v_target = _GetEnemyMoving(combat_distance)
            if v_target == 0 and not targeting_strict:
                v_target = nearest_enemy
        elif target_allegiance == Skilltarget.EnemyKnockedDown:
            v_target = _GetEnemyKnockedDown(combat_distance)
            if v_target == 0 and not targeting_strict:
                v_target = nearest_enemy           
        elif target_allegiance == Skilltarget.AllyMartialRanged:
            v_target = Routines.Agents.GetNearestEnemyRanged(combat_distance)
            if v_target == 0 and not targeting_strict:
                v_target = nearest_enemy
        elif target_allegiance == Skilltarget.Ally:
            v_target = lowest_ally
        elif target_allegiance == Skilltarget.AllyCaster:
            v_target = _TargetLowestAllyCaster(filter_skill_id=skills[slot].skill_id)
            if v_target == 0 and not targeting_strict:
                v_target = lowest_ally
        elif target_allegiance == Skilltarget.AllyMartial:
            v_target = _TargetLowestAllyMartial(filter_skill_id=skills[slot].skill_id)
            if v_target == 0 and not targeting_strict:
                v_target = lowest_ally
        elif target_allegiance == Skilltarget.AllyMartialMelee:
            v_target = _TargetLowestAllyMelee(filter_skill_id=skills[slot].skill_id)
            if v_target == 0 and not targeting_strict:
                v_target = lowest_ally
        elif target_allegiance == Skilltarget.AllyMartialRanged:
            v_target = _TargetLowestAllyRanged(filter_skill_id=skills[slot].skill_id)
            if v_target == 0 and not targeting_strict:
                v_target = lowest_ally
        elif target_allegiance == Skilltarget.OtherAlly:
            if skills[slot].custom_skill_data.Nature == SkillNature.EnergyBuff.value:
                v_target = _TargetLowestAllyEnergy(other_ally=True, filter_skill_id=skills[slot].skill_id)
                #print("Energy Buff Target: ", RawAgentArray().get_name(v_target))
            else:
                v_target = _TargetLowestAlly(other_ally=True, filter_skill_id=skills[slot].skill_id)
        elif target_allegiance == Skilltarget.Self:
            v_target = GLOBAL_CACHE.Player.GetAgentID()
        elif target_allegiance == Skilltarget.Pet:
            v_target = GLOBAL_CACHE.Party.Pets.GetPetID(GLOBAL_CACHE.Player.GetAgentID())
        elif target_allegiance == Skilltarget.DeadAlly:
            v_target = Routines.Agents.GetDeadAlly(Range.Spellcast.value)
        elif target_allegiance == Skilltarget.Spirit:
            v_target = Routines.Agents.GetNearestSpirit(Range.Spellcast.value)
        elif target_allegiance == Skilltarget.Minion:
            v_target = Routines.Agents.GetLowestMinion(Range.Spellcast.value)
        elif target_allegiance == Skilltarget.Corpse:
            v_target = Routines.Agents.GetNearestCorpse(Range.Spellcast.value)
        else:
            v_target = GetPartytarget_fn()
            if v_target == 0:
                v_target = nearest_enemy
        return v_target
    
def _AreCastConditionsMet(slot, 
                          vTarget, 
                          skills, 
                          unique_skills, 
                          HasEffect_fn, 
                          GetEnergyValues_fn, 
                          shared_memory_handler) -> bool:
    
        number_of_features = 0
        feature_count = 0

        Conditions = skills[slot].custom_skill_data.Conditions

        """ Check if the skill is a resurrection skill and the target is dead """
        if skills[slot].custom_skill_data.Nature == SkillNature.Resurrection.value:
            return True if GLOBAL_CACHE.Agent.IsDead(vTarget) else False


        if skills[slot].custom_skill_data.Conditions.UniqueProperty:
            """ check all UniqueProperty skills """
            if (skills[slot].skill_id == unique_skills.energy_drain or
                skills[slot].skill_id == unique_skills.energy_tap or
                skills[slot].skill_id == unique_skills.ether_lord
                ):
                return GetEnergyValues_fn(GLOBAL_CACHE.Player.GetAgentID()) < Conditions.LessEnergy

            if (skills[slot].skill_id == unique_skills.essence_strike):
                energy = GetEnergyValues_fn(GLOBAL_CACHE.Player.GetAgentID()) < Conditions.LessEnergy
                return energy and (Routines.Agents.GetNearestSpirit(Range.Spellcast.value) != 0)

            if (skills[slot].skill_id == unique_skills.glowing_signet):
                energy= GetEnergyValues_fn(GLOBAL_CACHE.Player.GetAgentID()) < Conditions.LessEnergy
                return energy and HasEffect_fn(vTarget, unique_skills.burning)

            if (skills[slot].skill_id == unique_skills.clamor_of_souls):
                energy = GetEnergyValues_fn(GLOBAL_CACHE.Player.GetAgentID()) < Conditions.LessEnergy
                weapon_type, _ = GLOBAL_CACHE.Agent.GetWeaponType(GLOBAL_CACHE.Player.GetAgentID())
                return energy and weapon_type == 0

            if (skills[slot].skill_id == unique_skills.waste_not_want_not):
                energy= GetEnergyValues_fn(GLOBAL_CACHE.Player.GetAgentID()) < Conditions.LessEnergy
                return energy and not GLOBAL_CACHE.Agent.IsCasting(vTarget) and not GLOBAL_CACHE.Agent.IsAttacking(vTarget)

            if (skills[slot].skill_id == unique_skills.mend_body_and_soul):
                spirits_exist = Routines.Agents.GetNearestSpirit(Range.Earshot.value)
                life = GLOBAL_CACHE.Agent.GetHealth(GLOBAL_CACHE.Player.GetAgentID()) < Conditions.LessLife
                result = life or (spirits_exist and GLOBAL_CACHE.Agent.IsConditioned(vTarget))
                return bool(result)

            if (skills[slot].skill_id == unique_skills.grenths_balance):
                life = GLOBAL_CACHE.Agent.GetHealth(GLOBAL_CACHE.Player.GetAgentID()) < Conditions.LessLife
                return life and GLOBAL_CACHE.Agent.GetHealth(GLOBAL_CACHE.Player.GetAgentID()) < GLOBAL_CACHE.Agent.GetHealth(vTarget)

            if (skills[slot].skill_id == unique_skills.deaths_retreat):
                return GLOBAL_CACHE.Agent.GetHealth(GLOBAL_CACHE.Player.GetAgentID()) < GLOBAL_CACHE.Agent.GetHealth(vTarget)

            if (skills[slot].skill_id == unique_skills.plague_sending or
                skills[slot].skill_id == unique_skills.plague_signet or
                skills[slot].skill_id == unique_skills.plague_touch
                ):
                return GLOBAL_CACHE.Agent.IsConditioned(GLOBAL_CACHE.Player.GetAgentID())

            if (skills[slot].skill_id == unique_skills.golden_fang_strike or
                skills[slot].skill_id == unique_skills.golden_fox_strike or
                skills[slot].skill_id == unique_skills.golden_lotus_strike or
                skills[slot].skill_id == unique_skills.golden_phoenix_strike or
                skills[slot].skill_id == unique_skills.golden_skull_strike
                ):
                return GLOBAL_CACHE.Agent.IsEnchanted(GLOBAL_CACHE.Player.GetAgentID())

            if (skills[slot].skill_id == unique_skills.brutal_weapon):
                return not GLOBAL_CACHE.Agent.IsEnchanted(GLOBAL_CACHE.Player.GetAgentID())

            if (skills[slot].skill_id == unique_skills.signet_of_removal):
                return not GLOBAL_CACHE.Agent.IsEnchanted(vTarget) and GLOBAL_CACHE.Agent.IsConditioned(vTarget)

            if (skills[slot].skill_id == unique_skills.dwaynas_kiss or
                skills[slot].skill_id == unique_skills.unnatural_signet or
                skills[slot].skill_id == unique_skills.toxic_chill
                ):
                return GLOBAL_CACHE.Agent.IsHexed(vTarget) or GLOBAL_CACHE.Agent.IsEnchanted(vTarget)

            if (skills[slot].skill_id == unique_skills.discord):
                return (GLOBAL_CACHE.Agent.IsHexed(vTarget) and GLOBAL_CACHE.Agent.IsConditioned(vTarget)) or (GLOBAL_CACHE.Agent.IsEnchanted(vTarget))

            if (skills[slot].skill_id == unique_skills.empathic_removal or
                skills[slot].skill_id == unique_skills.iron_palm or
                skills[slot].skill_id == unique_skills.melandrus_resilience or
                skills[slot].skill_id == unique_skills.necrosis or
                skills[slot].skill_id == unique_skills.peace_and_harmony or
                skills[slot].skill_id == unique_skills.purge_signet or
                skills[slot].skill_id == unique_skills.resilient_weapon
                ):
                return GLOBAL_CACHE.Agent.IsHexed(vTarget) or GLOBAL_CACHE.Agent.IsConditioned(vTarget)

            if (skills[slot].skill_id == unique_skills.gaze_from_beyond or
                skills[slot].skill_id == unique_skills.spirit_burn or
                skills[slot].skill_id == unique_skills.signet_of_ghostly_might
                ):
                return True if Routines.Agents.GetNearestSpirit(Range.Spellcast.value) != 0 else False

            if (skills[slot].skill_id == unique_skills.comfort_animal or
                skills[slot].skill_id == unique_skills.heal_as_one
                ):
                LessLife = GLOBAL_CACHE.Agent.GetHealth(vTarget) < Conditions.LessLife
                dead = GLOBAL_CACHE.Agent.IsDead(vTarget)
                return LessLife or dead

            if (skills[slot].skill_id == unique_skills.natures_blessing):
                player_life = GLOBAL_CACHE.Agent.GetHealth(GLOBAL_CACHE.Player.GetAgentID()) < Conditions.LessLife
                nearest_npc = Routines.Agents.GetNearestNPC(Range.Spirit.value)
                if nearest_npc == 0:
                    return player_life

                nearest_NPC_life = GLOBAL_CACHE.Agent.GetHealth(nearest_npc) < Conditions.LessLife
                return player_life or nearest_NPC_life

            if (skills[slot].skill_id == unique_skills.relentless_assault
                ):
                return GLOBAL_CACHE.Agent.IsHexed(GLOBAL_CACHE.Player.GetAgentID()) or GLOBAL_CACHE.Agent.IsConditioned(GLOBAL_CACHE.Player.GetAgentID())


            return True  # if no unique property is configured, return True for all UniqueProperty
        

        feature_count += (1 if Conditions.IsAlive else 0)
        feature_count += (1 if Conditions.HasCondition else 0)
        feature_count += (1 if Conditions.HasBleeding else 0)
        feature_count += (1 if Conditions.HasBlindness else 0)
        feature_count += (1 if Conditions.HasBurning else 0)
        feature_count += (1 if Conditions.HasCrackedArmor else 0)
        feature_count += (1 if Conditions.HasCrippled else 0)
        feature_count += (1 if Conditions.HasDazed else 0)
        feature_count += (1 if Conditions.HasDeepWound else 0)
        feature_count += (1 if Conditions.HasDisease else 0)
        feature_count += (1 if Conditions.HasPoison else 0)
        feature_count += (1 if Conditions.HasWeakness else 0)
        feature_count += (1 if Conditions.HasWeaponSpell else 0)
        feature_count += (1 if Conditions.HasEnchantment else 0)
        feature_count += (1 if Conditions.HasDervishEnchantment else 0)
        feature_count += (1 if Conditions.HasHex else 0)
        feature_count += (1 if Conditions.HasChant else 0)
        feature_count += (1 if Conditions.IsCasting else 0)
        feature_count += (1 if Conditions.IsKnockedDown else 0)
        feature_count += (1 if Conditions.IsMoving else 0)
        feature_count += (1 if Conditions.IsAttacking else 0)
        feature_count += (1 if Conditions.IsHoldingItem else 0)
        feature_count += (1 if Conditions.LessLife > 0 else 0)
        feature_count += (1 if Conditions.MoreLife > 0 else 0)
        feature_count += (1 if Conditions.LessEnergy > 0 else 0)
        feature_count += (1 if Conditions.Overcast > 0 else 0)
        feature_count += (1 if Conditions.IsPartyWide else 0)
        feature_count += (1 if Conditions.RequiresSpiritInEarshot else 0)
        feature_count += (1 if Conditions.EnemiesInRange > 0 else 0)
        feature_count += (1 if Conditions.AlliesInRange > 0 else 0)
        feature_count += (1 if Conditions.SpiritsInRange > 0 else 0)
        feature_count += (1 if Conditions.MinionsInRange > 0 else 0)

        if Conditions.IsAlive:
            if GLOBAL_CACHE.Agent.IsAlive(vTarget):
                number_of_features += 1

        is_conditioned = GLOBAL_CACHE.Agent.IsConditioned(vTarget)
        is_bleeding = GLOBAL_CACHE.Agent.IsBleeding(vTarget)
        is_blind = HasEffect_fn(vTarget, unique_skills.blind)
        is_burning = HasEffect_fn(vTarget, unique_skills.burning)
        is_cracked_armor = HasEffect_fn(vTarget, unique_skills.cracked_armor)
        is_crippled = GLOBAL_CACHE.Agent.IsCrippled(vTarget)
        is_dazed = HasEffect_fn(vTarget, unique_skills.dazed)
        is_deep_wound = HasEffect_fn(vTarget, unique_skills.deep_wound)
        is_disease = HasEffect_fn(vTarget, unique_skills.disease)
        is_poison = GLOBAL_CACHE.Agent.IsPoisoned(vTarget)
        is_weakness = HasEffect_fn(vTarget, unique_skills.weakness)

        if Conditions.HasCondition:
            if (is_conditioned or 
                is_bleeding or 
                is_blind or 
                is_burning or 
                is_cracked_armor or 
                is_crippled or 
                is_dazed or 
                is_deep_wound or 
                is_disease or 
                is_poison or 
                is_weakness):
                number_of_features += 1


        if Conditions.HasBleeding:
            if is_bleeding:
                number_of_features += 1

        if Conditions.HasBlindness:
            if is_blind:
                number_of_features += 1

        if Conditions.HasBurning:
            if is_burning:
                number_of_features += 1

        if Conditions.HasCrackedArmor:
            if is_cracked_armor:
                number_of_features += 1
          
        if Conditions.HasCrippled:
            if is_crippled:
                number_of_features += 1
                
        if Conditions.HasDazed:
            if is_dazed:
                number_of_features += 1
          
        if Conditions.HasDeepWound:
            if is_deep_wound:
                number_of_features += 1
                
        if Conditions.HasDisease:
            if is_disease:
                number_of_features += 1

        if Conditions.HasPoison:
            if is_poison:
                number_of_features += 1

        if Conditions.HasWeakness:
            if is_weakness:
                number_of_features += 1
         
        if Conditions.HasWeaponSpell:
            if GLOBAL_CACHE.Agent.IsWeaponSpelled(vTarget):
                if len(Conditions.WeaponSpellList) == 0:
                    number_of_features += 1
                else:
                    for skill_id in Conditions.WeaponSpellList:
                        if HasEffect_fn(vTarget, skill_id, exact_weapon_spell=True):
                            number_of_features += 1
                            break

        if Conditions.HasEnchantment:
            if GLOBAL_CACHE.Agent.IsEnchanted(vTarget):
                if len(Conditions.EnchantmentList) == 0:
                    number_of_features += 1
                else:
                    for skill_id in Conditions.EnchantmentList:
                        if HasEffect_fn(vTarget, skill_id):
                            number_of_features += 1
                            break

        if Conditions.HasDervishEnchantment:
            buff_list = self.shared_memory_handler.get_agent_buffs(GLOBAL_CACHE.Player.GetAgentID())
            for buff in buff_list:
                skill_type, _ = GLOBAL_CACHE.Skill.GetType(buff)
                if skill_type == SkillType.Enchantment.value:
                    _, profession = GLOBAL_CACHE.Skill.GetProfession(buff)
                    if profession == "Dervish":
                        number_of_features += 1
                        break

        if Conditions.HasHex:
            if GLOBAL_CACHE.Agent.IsHexed(vTarget):
                if len(Conditions.HexList) == 0:
                    number_of_features += 1
                else:
                    for skill_id in Conditions.HexList:
                        if self.HasEffect(vTarget, skill_id):
                            number_of_features += 1
                            break

        if Conditions.HasChant:
            if self.IsPartyMember(vTarget):
                buff_list = self.shared_memory_handler.get_agent_buffs(vTarget)
                for buff in buff_list:
                    skill_type, _ = GLOBAL_CACHE.Skill.GetType(buff)
                    if skill_type == SkillType.Chant.value:
                        if len(Conditions.ChantList) == 0:
                            number_of_features += 1
                        else:
                            if buff in Conditions.ChantList:
                                number_of_features += 1
                                break
                                
        if Conditions.IsCasting:
            if GLOBAL_CACHE.Agent.IsCasting(vTarget):
                casting_skill_id = GLOBAL_CACHE.Agent.GetCastingSkill(vTarget)
                if GLOBAL_CACHE.Skill.Data.GetActivation(casting_skill_id) >= 0.250:
                    if len(Conditions.CastingSkillList) == 0:
                        number_of_features += 1
                    else:
                        if casting_skill_id in Conditions.CastingSkillList:
                            number_of_features += 1

        if Conditions.IsKnockedDown:
            if GLOBAL_CACHE.Agent.IsKnockedDown(vTarget):
                number_of_features += 1
                            
        if Conditions.IsMoving:
            if GLOBAL_CACHE.Agent.IsMoving(vTarget):
                number_of_features += 1
        
        if Conditions.IsAttacking:
            if GLOBAL_CACHE.Agent.IsAttacking(vTarget):
                number_of_features += 1

        if Conditions.IsHoldingItem:
            weapon_type, _ = GLOBAL_CACHE.Agent.GetWeaponType(vTarget)
            if weapon_type == 0:
                number_of_features += 1

        if Conditions.LessLife != 0:
            if GLOBAL_CACHE.Agent.GetHealth(vTarget) < Conditions.LessLife:
                number_of_features += 1

        if Conditions.MoreLife != 0:
            if GLOBAL_CACHE.Agent.GetHealth(vTarget) > Conditions.MoreLife:
                number_of_features += 1
        
        if Conditions.LessEnergy != 0:
            if self.IsPartyMember(vTarget):
                for i in range(MAX_NUM_PLAYERS):
                    player_data = self.shared_memory_handler.get_player(i)
                    if player_data and player_data["IsActive"] and player_data["PlayerID"] == vTarget:
                        if player_data["Energy"] < Conditions.LessEnergy:
                            number_of_features += 1
            else:
                number_of_features += 1 #henchmen, allies, pets or something else thats not reporting energy

        if Conditions.Overcast != 0:
            if GLOBAL_CACHE.Player.GetAgentID() == vTarget:
                if GLOBAL_CACHE.Agent.GetOvercast(vTarget) < Conditions.Overcast:
                    number_of_features += 1
                    
        if Conditions.IsPartyWide:
            area = Range.SafeCompass.value if Conditions.PartyWideArea == 0 else Conditions.PartyWideArea
            less_life = Conditions.LessLife
            
            allies_array = GetAllAlliesArray(area)
            total_group_life = 0.0
            for agent in allies_array:
                total_group_life += GLOBAL_CACHE.Agent.GetHealth(agent)
                
            total_group_life /= len(allies_array)
            
            if total_group_life < less_life:
                number_of_features += 1
                                    
        if Conditions.RequiresSpiritInEarshot:            
            distance = Range.Earshot.value
            spirit_array = GLOBAL_CACHE.AgentArray.GetSpiritPetArray()
            spirit_array = AgentArray.Filter.ByDistance(spirit_array, GLOBAL_CACHE.Player.GetXY(), distance)            
            spirit_array = AgentArray.Filter.ByCondition(spirit_array, lambda agent_id: GLOBAL_CACHE.Agent.IsAlive(agent_id))
            
            if(len(spirit_array) > 0):
                number_of_features += 1
                    
        if skills[slot].custom_skill_data.SkillType == SkillType.PetAttack.value:
            pet_id = GLOBAL_CACHE.Party.Pets.GetPetID(GLOBAL_CACHE.Player.GetAgentID())
            if GLOBAL_CACHE.Agent.IsDead(pet_id):
                return False
            
            pet_attack_list = [GLOBAL_CACHE.Skill.GetID("Bestial_Mauling"),
                               GLOBAL_CACHE.Skill.GetID("Bestial_Pounce"),
                               GLOBAL_CACHE.Skill.GetID("Brutal_Strike"),
                               GLOBAL_CACHE.Skill.GetID("Disrupting_Lunge"),
                               GLOBAL_CACHE.Skill.GetID("Enraged_Lunge"),
                               GLOBAL_CACHE.Skill.GetID("Feral_Lunge"),
                               GLOBAL_CACHE.Skill.GetID("Ferocious_Strike"),
                               GLOBAL_CACHE.Skill.GetID("Maiming_Strike"),
                               GLOBAL_CACHE.Skill.GetID("Melandrus_Assault"),
                               GLOBAL_CACHE.Skill.GetID("Poisonous_Bite"),
                               GLOBAL_CACHE.Skill.GetID("Pounce"),
                               GLOBAL_CACHE.Skill.GetID("Predators_Pounce"),
                               GLOBAL_CACHE.Skill.GetID("Savage_Pounce"),
                               GLOBAL_CACHE.Skill.GetID("Scavenger_Strike")
                               ]
            
            for skill_id in pet_attack_list:
                if skills[slot].skill_id == skill_id:
                    if self.HasEffect(pet_id,skills[slot].skill_id ):
                        return False
            
        if Conditions.EnemiesInRange != 0:
            player_pos = GLOBAL_CACHE.Player.GetXY()
            enemy_array = enemy_array = Routines.Agents.GetFilteredEnemyArray(player_pos[0], player_pos[1], Conditions.EnemiesInRangeArea)
            if len(enemy_array) >= Conditions.EnemiesInRange:
                number_of_features += 1
            else:
                number_of_features = 0
                
        if Conditions.AlliesInRange != 0:
            player_pos = GLOBAL_CACHE.Player.GetXY()
            ally_array = ally_array = Routines.Agents.GetFilteredAllyArray(player_pos[0], player_pos[1], Conditions.AlliesInRangeArea,other_ally=True)
            if len(ally_array) >= Conditions.AlliesInRange:
                number_of_features += 1
            else:
                number_of_features = 0
                
        if Conditions.SpiritsInRange != 0:
            player_pos = GLOBAL_CACHE.Player.GetXY()
            ally_array = ally_array = Routines.Agents.GetFilteredSpiritArray(player_pos[0], player_pos[1], Conditions.SpiritsInRangeArea)
            if len(ally_array) >= Conditions.SpiritsInRange:
                number_of_features += 1
            else:
                number_of_features = 0
                
        if Conditions.MinionsInRange != 0:
            player_pos = GLOBAL_CACHE.Player.GetXY()
            ally_array = ally_array = Routines.Agents.GetFilteredMinionArray(player_pos[0], player_pos[1], Conditions.MinionsInRangeArea)
            if len(ally_array) >= Conditions.MinionsInRange:
                number_of_features += 1
            else:
                number_of_features = 0
            

        #Py4GW.Console.Log("AreCastConditionsMet", f"feature count: {feature_count}, No of features {number_of_features}", Py4GW.Console.MessageType.Info)
        
        if feature_count == number_of_features:
            return True

        return False



class CombatClass:
    global MAX_SKILLS, custom_skill_data_handler

    class SkillData:
        def __init__(self, slot):
            self.skill_id = GLOBAL_CACHE.SkillBar.GetSkillIDBySlot(slot)  # slot is 1 based
            self.skillbar_data = GLOBAL_CACHE.SkillBar.GetSkillData(slot)  # Fetch additional data from the skill bar
            self.custom_skill_data = custom_skill_data_handler.get_skill(self.skill_id)  # Retrieve custom skill data

    def __init__(self):
        import HeroAI.shared_memory_manager as shared_memory_manager
        """
        Initializes the CombatClass with an empty skill set and order.
        """
        self.skills = []
        self.skill_order = [0] * MAX_SKILLS
        self.skill_pointer = 0
        self.in_casting_routine = False
        self.aftercast = 0
        self.aftercast_timer = ThrottledTimer()
        self.aftercast_timer.Start()
        self.ping_handler = Py4GW.PingHandler()
        self.oldCalledTarget = 0
        self.shared_memory_handler = shared_memory_manager.SharedMemoryManager()
        
        self.in_aggro = False
        self.is_targeting_enabled = False
        self.is_combat_enabled = False
        self.is_skill_enabled = []
        self.fast_casting_exists = False
        self.fast_casting_level = 0
        self.expertise_exists = False
        self.expertise_level = 0
        
        self.nearest_enemy = Routines.Agents.GetNearestEnemy(self.get_combat_distance())
        self.lowest_ally = TargetLowestAlly()
        self.lowest_ally_energy = TargetLowestAllyEnergy()
        self.nearest_npc = Routines.Agents.GetNearestNPC(Range.Spellcast.value)
        self.nearest_spirit = Routines.Agents.GetNearestSpirit(Range.Spellcast.value)
        self.lowest_minion = Routines.Agents.GetLowestMinion(Range.Spellcast.value)
        self.nearest_corpse = Routines.Agents.GetNearestCorpse(Range.Spellcast.value)
        
        self.unique_skills = UniqueSkills()
        
    def Update(self, cached_data):
        self.in_aggro = cached_data.in_aggro
        self.is_targeting_enabled = cached_data.is_targeting_enabled
        self.is_combat_enabled = cached_data.is_combat_enabled
        self.is_skill_enabled = cached_data.is_skill_enabled
        self.fast_casting_exists = cached_data.fast_casting_exists
        self.fast_casting_level = cached_data.fast_casting_level
        self.expertise_exists = cached_data.expertise_exists
        self.expertise_level = cached_data.expertise_level
        
    def PrioritizeSkills(self):
        """
        Create a priority-based skill execution order.
        """
        self.skills = _PrioritizeSkills(self.SkillData, self.skill_order)

    def GetSkills(self):
        """
        Retrieve the prioritized skill set.
        """
        return self.skills
        
    def GetOrderedSkill(self, index:int)-> Optional[SkillData]:
        """
        Retrieve the skill at the given index in the prioritized order.
        """
        if 0 <= index < MAX_SKILLS:
            return self.skills[index]
        return None  # Return None if the index is out of bounds

    def AdvanceSkillPointer(self):
        self.skill_pointer += 1
        if self.skill_pointer >= MAX_SKILLS:
            self.skill_pointer = 0
            
    def ResetSkillPointer(self):
        self.skill_pointer = 0
        
    def SetSkillPointer(self, pointer):
        if 0 <= pointer < MAX_SKILLS:
            self.skill_pointer = pointer
        else:
            self.skill_pointer = 0
            
    def GetSkillPointer(self):
        return self.skill_pointer
            
    def GetEnergyValues(self,agent_id):
        for i in range(MAX_NUM_PLAYERS):
            player_data = self.shared_memory_handler.get_player(i)
            if player_data and player_data["IsActive"] and player_data["PlayerID"] == agent_id:
                return player_data["Energy"]
        return 1.0 #default return full energy to prevent issues

    def IsSkillReady(self, slot):
        return _IsSkillReady(slot, self.skill_order, self.skills, self.is_skill_enabled)
        
    def InCastingRoutine(self):
        return _InCastingRoutine(self.aftercast_timer, self.in_casting_routine)
 
    def GetPartyTargetID(self):
        return Routines.Party.GetPartyTargetID()


    def SafeChangeTarget(self, target_id):
        Routines.Targeting.SafeChangeTarget(target_id)
            
    def SafeInteract(self, target_id):
        Routines.Agents.SafeInteract(target_id)


    def GetPartyTarget(self):
        if not self.is_combat_enabled:
            return 0

        if not self.is_targeting_enabled:
            return 0
        
        return _GetPartyTarget()


    def get_combat_distance(self):
        return Range.Spellcast.value if self.in_aggro else Range.Earshot.value

    def GetAppropiateTarget(self, slot):
        return _GetAppropiateTarget(
            self.skills,
            self.unique_skills,
            self.HasEffect,
            self.GetPartyTarget,
            multibox=True,
            slot=slot,
            is_targeting_enabled=self.is_targeting_enabled,
            is_combat_enabled=self.is_combat_enabled,
            combat_distance=self.get_combat_distance(),
        )
        

    def IsPartyMember(self, agent_id):
        for i in range(MAX_NUM_PLAYERS):
            player_data = self.shared_memory_handler.get_player(i)
            if player_data and player_data["IsActive"] and player_data["PlayerID"] == agent_id:
                return True
            
        allegiance , _ = GLOBAL_CACHE.Agent.GetAllegiance(agent_id)
        if (allegiance == Allegiance.SpiritPet.value and 
            not GLOBAL_CACHE.Agent.IsSpawned(agent_id)):
            return True
        
        return False
        
    def HasEffect(self, agent_id, skill_id, exact_weapon_spell=False):

        result = False
        custom_skill_data = custom_skill_data_handler.get_skill(skill_id)
        shared_effects = getattr(custom_skill_data.Conditions, "SharedEffects", []) if custom_skill_data else []


        if self.IsPartyMember(agent_id):
            player_buffs = self.shared_memory_handler.get_agent_buffs(agent_id)
            for buff in player_buffs:                
                if buff == skill_id or buff in shared_effects:
                    result = True
        else:
            result = (
                GLOBAL_CACHE.Effects.BuffExists(agent_id, skill_id) 
                or GLOBAL_CACHE.Effects.EffectExists(agent_id, skill_id)
                or any(GLOBAL_CACHE.Effects.BuffExists(agent_id, shared_buff) or GLOBAL_CACHE.Effects.EffectExists(agent_id, shared_buff) for shared_buff in shared_effects))

        if not result and not exact_weapon_spell:
           skilltype, _ = GLOBAL_CACHE.Skill.GetType(skill_id)
           if skilltype == SkillType.WeaponSpell.value:
               result = GLOBAL_CACHE.Agent.IsWeaponSpelled(agent_id)

        return result


    def AreCastConditionsMet(self, slot, vTarget):
        number_of_features = 0
        feature_count = 0

        Conditions = self.skills[slot].custom_skill_data.Conditions

        """ Check if the skill is a resurrection skill and the target is dead """
        if self.skills[slot].custom_skill_data.Nature == SkillNature.Resurrection.value:
            return True if GLOBAL_CACHE.Agent.IsDead(vTarget) else False


        if self.skills[slot].custom_skill_data.Conditions.UniqueProperty:
            """ check all UniqueProperty skills """
            if (self.skills[slot].skill_id == self.unique_skills.energy_drain or
                self.skills[slot].skill_id == self.unique_skills.energy_tap or
                self.skills[slot].skill_id == self.unique_skills.ether_lord
                ):
                return self.GetEnergyValues(GLOBAL_CACHE.Player.GetAgentID()) < Conditions.LessEnergy

            if (self.skills[slot].skill_id == self.unique_skills.essence_strike):
                energy = self.GetEnergyValues(GLOBAL_CACHE.Player.GetAgentID()) < Conditions.LessEnergy
                return energy and (Routines.Agents.GetNearestSpirit(Range.Spellcast.value) != 0)

            if (self.skills[slot].skill_id == self.unique_skills.glowing_signet):
                energy= self.GetEnergyValues(GLOBAL_CACHE.Player.GetAgentID()) < Conditions.LessEnergy
                return energy and self.HasEffect(vTarget, self.unique_skills.burning)

            if (self.skills[slot].skill_id == self.unique_skills.clamor_of_souls):
                energy = self.GetEnergyValues(GLOBAL_CACHE.Player.GetAgentID()) < Conditions.LessEnergy
                weapon_type, _ = GLOBAL_CACHE.Agent.GetWeaponType(GLOBAL_CACHE.Player.GetAgentID())
                return energy and weapon_type == 0

            if (self.skills[slot].skill_id == self.unique_skills.waste_not_want_not):
                energy= self.GetEnergyValues(GLOBAL_CACHE.Player.GetAgentID()) < Conditions.LessEnergy
                return energy and not GLOBAL_CACHE.Agent.IsCasting(vTarget) and not GLOBAL_CACHE.Agent.IsAttacking(vTarget)

            if (self.skills[slot].skill_id == self.unique_skills.mend_body_and_soul):
                spirits_exist = Routines.Agents.GetNearestSpirit(Range.Earshot.value)
                life = GLOBAL_CACHE.Agent.GetHealth(GLOBAL_CACHE.Player.GetAgentID()) < Conditions.LessLife
                return life or (spirits_exist and GLOBAL_CACHE.Agent.IsConditioned(vTarget))

            if (self.skills[slot].skill_id == self.unique_skills.grenths_balance):
                life = GLOBAL_CACHE.Agent.GetHealth(GLOBAL_CACHE.Player.GetAgentID()) < Conditions.LessLife
                return life and GLOBAL_CACHE.Agent.GetHealth(GLOBAL_CACHE.Player.GetAgentID()) < GLOBAL_CACHE.Agent.GetHealth(vTarget)

            if (self.skills[slot].skill_id == self.unique_skills.deaths_retreat):
                return GLOBAL_CACHE.Agent.GetHealth(GLOBAL_CACHE.Player.GetAgentID()) < GLOBAL_CACHE.Agent.GetHealth(vTarget)

            if (self.skills[slot].skill_id == self.unique_skills.plague_sending or
                self.skills[slot].skill_id == self.unique_skills.plague_signet or
                self.skills[slot].skill_id == self.unique_skills.plague_touch
                ):
                return GLOBAL_CACHE.Agent.IsConditioned(GLOBAL_CACHE.Player.GetAgentID())

            if (self.skills[slot].skill_id == self.unique_skills.golden_fang_strike or
                self.skills[slot].skill_id == self.unique_skills.golden_fox_strike or
                self.skills[slot].skill_id == self.unique_skills.golden_lotus_strike or
                self.skills[slot].skill_id == self.unique_skills.golden_phoenix_strike or
                self.skills[slot].skill_id == self.unique_skills.golden_skull_strike
                ):
                return GLOBAL_CACHE.Agent.IsEnchanted(GLOBAL_CACHE.Player.GetAgentID())

            if (self.skills[slot].skill_id == self.unique_skills.brutal_weapon):
                return not GLOBAL_CACHE.Agent.IsEnchanted(GLOBAL_CACHE.Player.GetAgentID())

            if (self.skills[slot].skill_id == self.unique_skills.signet_of_removal):
                return not GLOBAL_CACHE.Agent.IsEnchanted(vTarget) and GLOBAL_CACHE.Agent.IsConditioned(vTarget)

            if (self.skills[slot].skill_id == self.unique_skills.dwaynas_kiss or
                self.skills[slot].skill_id == self.unique_skills.unnatural_signet or
                self.skills[slot].skill_id == self.unique_skills.toxic_chill
                ):
                return GLOBAL_CACHE.Agent.IsHexed(vTarget) or GLOBAL_CACHE.Agent.IsEnchanted(vTarget)

            if (self.skills[slot].skill_id == self.unique_skills.discord):
                return (GLOBAL_CACHE.Agent.IsHexed(vTarget) and GLOBAL_CACHE.Agent.IsConditioned(vTarget)) or (GLOBAL_CACHE.Agent.IsEnchanted(vTarget))

            if (self.skills[slot].skill_id == self.unique_skills.empathic_removal or
                self.skills[slot].skill_id == self.unique_skills.iron_palm or
                self.skills[slot].skill_id == self.unique_skills.melandrus_resilience or
                self.skills[slot].skill_id == self.unique_skills.necrosis or
                self.skills[slot].skill_id == self.unique_skills.peace_and_harmony or
                self.skills[slot].skill_id == self.unique_skills.purge_signet or
                self.skills[slot].skill_id == self.unique_skills.resilient_weapon
                ):
                return GLOBAL_CACHE.Agent.IsHexed(vTarget) or GLOBAL_CACHE.Agent.IsConditioned(vTarget)

            if (self.skills[slot].skill_id == self.unique_skills.gaze_from_beyond or
                self.skills[slot].skill_id == self.unique_skills.spirit_burn or
                self.skills[slot].skill_id == self.unique_skills.signet_of_ghostly_might
                ):
                return True if Routines.Agents.GetNearestSpirit(Range.Spellcast.value) != 0 else False

            if (self.skills[slot].skill_id == self.unique_skills.comfort_animal or
                self.skills[slot].skill_id == self.unique_skills.heal_as_one
                ):
                LessLife = GLOBAL_CACHE.Agent.GetHealth(vTarget) < Conditions.LessLife
                dead = GLOBAL_CACHE.Agent.IsDead(vTarget)
                return LessLife or dead

            if (self.skills[slot].skill_id == self.unique_skills.natures_blessing):
                player_life = GLOBAL_CACHE.Agent.GetHealth(GLOBAL_CACHE.Player.GetAgentID()) < Conditions.LessLife
                nearest_npc = Routines.Agents.GetNearestNPC(Range.Spirit.value)
                if nearest_npc == 0:
                    return player_life

                nearest_NPC_life = GLOBAL_CACHE.Agent.GetHealth(nearest_npc) < Conditions.LessLife
                return player_life or nearest_NPC_life

            if (self.skills[slot].skill_id == self.unique_skills.relentless_assault
                ):
                return GLOBAL_CACHE.Agent.IsHexed(GLOBAL_CACHE.Player.GetAgentID()) or GLOBAL_CACHE.Agent.IsConditioned(GLOBAL_CACHE.Player.GetAgentID())


            return True  # if no unique property is configured, return True for all UniqueProperty
        

        feature_count += (1 if Conditions.IsAlive else 0)
        feature_count += (1 if Conditions.HasCondition else 0)
        feature_count += (1 if Conditions.HasBleeding else 0)
        feature_count += (1 if Conditions.HasBlindness else 0)
        feature_count += (1 if Conditions.HasBurning else 0)
        feature_count += (1 if Conditions.HasCrackedArmor else 0)
        feature_count += (1 if Conditions.HasCrippled else 0)
        feature_count += (1 if Conditions.HasDazed else 0)
        feature_count += (1 if Conditions.HasDeepWound else 0)
        feature_count += (1 if Conditions.HasDisease else 0)
        feature_count += (1 if Conditions.HasPoison else 0)
        feature_count += (1 if Conditions.HasWeakness else 0)
        feature_count += (1 if Conditions.HasWeaponSpell else 0)
        feature_count += (1 if Conditions.HasEnchantment else 0)
        feature_count += (1 if Conditions.HasDervishEnchantment else 0)
        feature_count += (1 if Conditions.HasHex else 0)
        feature_count += (1 if Conditions.HasChant else 0)
        feature_count += (1 if Conditions.IsCasting else 0)
        feature_count += (1 if Conditions.IsKnockedDown else 0)
        feature_count += (1 if Conditions.IsMoving else 0)
        feature_count += (1 if Conditions.IsAttacking else 0)
        feature_count += (1 if Conditions.IsHoldingItem else 0)
        feature_count += (1 if Conditions.LessLife > 0 else 0)
        feature_count += (1 if Conditions.MoreLife > 0 else 0)
        feature_count += (1 if Conditions.LessEnergy > 0 else 0)
        feature_count += (1 if Conditions.Overcast > 0 else 0)
        feature_count += (1 if Conditions.IsPartyWide else 0)
        feature_count += (1 if Conditions.RequiresSpiritInEarshot else 0)
        feature_count += (1 if Conditions.EnemiesInRange > 0 else 0)
        feature_count += (1 if Conditions.AlliesInRange > 0 else 0)
        feature_count += (1 if Conditions.SpiritsInRange > 0 else 0)
        feature_count += (1 if Conditions.MinionsInRange > 0 else 0)

        if Conditions.IsAlive:
            if GLOBAL_CACHE.Agent.IsAlive(vTarget):
                number_of_features += 1

        is_conditioned = GLOBAL_CACHE.Agent.IsConditioned(vTarget)
        is_bleeding = GLOBAL_CACHE.Agent.IsBleeding(vTarget)
        is_blind = self.HasEffect(vTarget, self.unique_skills.blind)
        is_burning = self.HasEffect(vTarget, self.unique_skills.burning)
        is_cracked_armor = self.HasEffect(vTarget, self.unique_skills.cracked_armor)
        is_crippled = GLOBAL_CACHE.Agent.IsCrippled(vTarget)
        is_dazed = self.HasEffect(vTarget, self.unique_skills.dazed)
        is_deep_wound = self.HasEffect(vTarget, self.unique_skills.deep_wound)
        is_disease = self.HasEffect(vTarget, self.unique_skills.disease)
        is_poison = GLOBAL_CACHE.Agent.IsPoisoned(vTarget)
        is_weakness = self.HasEffect(vTarget, self.unique_skills.weakness)

        if Conditions.HasCondition:
            if (is_conditioned or 
                is_bleeding or 
                is_blind or 
                is_burning or 
                is_cracked_armor or 
                is_crippled or 
                is_dazed or 
                is_deep_wound or 
                is_disease or 
                is_poison or 
                is_weakness):
                number_of_features += 1


        if Conditions.HasBleeding:
            if is_bleeding:
                number_of_features += 1

        if Conditions.HasBlindness:
            if is_blind:
                number_of_features += 1

        if Conditions.HasBurning:
            if is_burning:
                number_of_features += 1

        if Conditions.HasCrackedArmor:
            if is_cracked_armor:
                number_of_features += 1
          
        if Conditions.HasCrippled:
            if is_crippled:
                number_of_features += 1
                
        if Conditions.HasDazed:
            if is_dazed:
                number_of_features += 1
          
        if Conditions.HasDeepWound:
            if is_deep_wound:
                number_of_features += 1
                
        if Conditions.HasDisease:
            if is_disease:
                number_of_features += 1

        if Conditions.HasPoison:
            if is_poison:
                number_of_features += 1

        if Conditions.HasWeakness:
            if is_weakness:
                number_of_features += 1
         
        if Conditions.HasWeaponSpell:
            if GLOBAL_CACHE.Agent.IsWeaponSpelled(vTarget):
                if len(Conditions.WeaponSpellList) == 0:
                    number_of_features += 1
                else:
                    for skill_id in Conditions.WeaponSpellList:
                        if self.HasEffect(vTarget, skill_id, exact_weapon_spell=True):
                            number_of_features += 1
                            break

        if Conditions.HasEnchantment:
            if GLOBAL_CACHE.Agent.IsEnchanted(vTarget):
                if len(Conditions.EnchantmentList) == 0:
                    number_of_features += 1
                else:
                    for skill_id in Conditions.EnchantmentList:
                        if self.HasEffect(vTarget, skill_id):
                            number_of_features += 1
                            break

        if Conditions.HasDervishEnchantment:
            buff_list = self.shared_memory_handler.get_agent_buffs(GLOBAL_CACHE.Player.GetAgentID())
            for buff in buff_list:
                skill_type, _ = GLOBAL_CACHE.Skill.GetType(buff)
                if skill_type == SkillType.Enchantment.value:
                    _, profession = GLOBAL_CACHE.Skill.GetProfession(buff)
                    if profession == "Dervish":
                        number_of_features += 1
                        break

        if Conditions.HasHex:
            if GLOBAL_CACHE.Agent.IsHexed(vTarget):
                if len(Conditions.HexList) == 0:
                    number_of_features += 1
                else:
                    for skill_id in Conditions.HexList:
                        if self.HasEffect(vTarget, skill_id):
                            number_of_features += 1
                            break

        if Conditions.HasChant:
            if self.IsPartyMember(vTarget):
                buff_list = self.shared_memory_handler.get_agent_buffs(vTarget)
                for buff in buff_list:
                    skill_type, _ = GLOBAL_CACHE.Skill.GetType(buff)
                    if skill_type == SkillType.Chant.value:
                        if len(Conditions.ChantList) == 0:
                            number_of_features += 1
                        else:
                            if buff in Conditions.ChantList:
                                number_of_features += 1
                                break
                                
        if Conditions.IsCasting:
            if GLOBAL_CACHE.Agent.IsCasting(vTarget):
                casting_skill_id = GLOBAL_CACHE.Agent.GetCastingSkill(vTarget)
                if GLOBAL_CACHE.Skill.Data.GetActivation(casting_skill_id) >= 0.250:
                    if len(Conditions.CastingSkillList) == 0:
                        number_of_features += 1
                    else:
                        if casting_skill_id in Conditions.CastingSkillList:
                            number_of_features += 1

        if Conditions.IsKnockedDown:
            if GLOBAL_CACHE.Agent.IsKnockedDown(vTarget):
                number_of_features += 1
                            
        if Conditions.IsMoving:
            if GLOBAL_CACHE.Agent.IsMoving(vTarget):
                number_of_features += 1
        
        if Conditions.IsAttacking:
            if GLOBAL_CACHE.Agent.IsAttacking(vTarget):
                number_of_features += 1

        if Conditions.IsHoldingItem:
            weapon_type, _ = GLOBAL_CACHE.Agent.GetWeaponType(vTarget)
            if weapon_type == 0:
                number_of_features += 1

        if Conditions.LessLife != 0:
            if GLOBAL_CACHE.Agent.GetHealth(vTarget) < Conditions.LessLife:
                number_of_features += 1

        if Conditions.MoreLife != 0:
            if GLOBAL_CACHE.Agent.GetHealth(vTarget) > Conditions.MoreLife:
                number_of_features += 1
        
        if Conditions.LessEnergy != 0:
            if self.IsPartyMember(vTarget):
                for i in range(MAX_NUM_PLAYERS):
                    player_data = self.shared_memory_handler.get_player(i)
                    if player_data and player_data["IsActive"] and player_data["PlayerID"] == vTarget:
                        if player_data["Energy"] < Conditions.LessEnergy:
                            number_of_features += 1
            else:
                number_of_features += 1 #henchmen, allies, pets or something else thats not reporting energy

        if Conditions.Overcast != 0:
            if GLOBAL_CACHE.Player.GetAgentID() == vTarget:
                if GLOBAL_CACHE.Agent.GetOvercast(vTarget) < Conditions.Overcast:
                    number_of_features += 1
                    
        if Conditions.IsPartyWide:
            area = Range.SafeCompass.value if Conditions.PartyWideArea == 0 else Conditions.PartyWideArea
            less_life = Conditions.LessLife
            
            allies_array = GetAllAlliesArray(area)
            total_group_life = 0.0
            for agent in allies_array:
                total_group_life += GLOBAL_CACHE.Agent.GetHealth(agent)
                
            total_group_life /= len(allies_array)
            
            if total_group_life < less_life:
                number_of_features += 1
                                    
        if Conditions.RequiresSpiritInEarshot:            
            distance = Range.Earshot.value
            spirit_array = GLOBAL_CACHE.AgentArray.GetSpiritPetArray()
            spirit_array = AgentArray.Filter.ByDistance(spirit_array, GLOBAL_CACHE.Player.GetXY(), distance)            
            spirit_array = AgentArray.Filter.ByCondition(spirit_array, lambda agent_id: GLOBAL_CACHE.Agent.IsAlive(agent_id))
            
            if(len(spirit_array) > 0):
                number_of_features += 1
                    
        if self.skills[slot].custom_skill_data.SkillType == SkillType.PetAttack.value:
            pet_id = GLOBAL_CACHE.Party.Pets.GetPetID(GLOBAL_CACHE.Player.GetAgentID())
            if GLOBAL_CACHE.Agent.IsDead(pet_id):
                return False
            
            pet_attack_list = [GLOBAL_CACHE.Skill.GetID("Bestial_Mauling"),
                               GLOBAL_CACHE.Skill.GetID("Bestial_Pounce"),
                               GLOBAL_CACHE.Skill.GetID("Brutal_Strike"),
                               GLOBAL_CACHE.Skill.GetID("Disrupting_Lunge"),
                               GLOBAL_CACHE.Skill.GetID("Enraged_Lunge"),
                               GLOBAL_CACHE.Skill.GetID("Feral_Lunge"),
                               GLOBAL_CACHE.Skill.GetID("Ferocious_Strike"),
                               GLOBAL_CACHE.Skill.GetID("Maiming_Strike"),
                               GLOBAL_CACHE.Skill.GetID("Melandrus_Assault"),
                               GLOBAL_CACHE.Skill.GetID("Poisonous_Bite"),
                               GLOBAL_CACHE.Skill.GetID("Pounce"),
                               GLOBAL_CACHE.Skill.GetID("Predators_Pounce"),
                               GLOBAL_CACHE.Skill.GetID("Savage_Pounce"),
                               GLOBAL_CACHE.Skill.GetID("Scavenger_Strike")
                               ]
            
            for skill_id in pet_attack_list:
                if self.skills[slot].skill_id == skill_id:
                    if self.HasEffect(pet_id,self.skills[slot].skill_id ):
                        return False
            
        if Conditions.EnemiesInRange != 0:
            player_pos = GLOBAL_CACHE.Player.GetXY()
            enemy_array = enemy_array = Routines.Agents.GetFilteredEnemyArray(player_pos[0], player_pos[1], Conditions.EnemiesInRangeArea)
            if len(enemy_array) >= Conditions.EnemiesInRange:
                number_of_features += 1
            else:
                number_of_features = 0
                
        if Conditions.AlliesInRange != 0:
            player_pos = GLOBAL_CACHE.Player.GetXY()
            ally_array = ally_array = Routines.Agents.GetFilteredAllyArray(player_pos[0], player_pos[1], Conditions.AlliesInRangeArea,other_ally=True)
            if len(ally_array) >= Conditions.AlliesInRange:
                number_of_features += 1
            else:
                number_of_features = 0
                
        if Conditions.SpiritsInRange != 0:
            player_pos = GLOBAL_CACHE.Player.GetXY()
            ally_array = ally_array = Routines.Agents.GetFilteredSpiritArray(player_pos[0], player_pos[1], Conditions.SpiritsInRangeArea)
            if len(ally_array) >= Conditions.SpiritsInRange:
                number_of_features += 1
            else:
                number_of_features = 0
                
        if Conditions.MinionsInRange != 0:
            player_pos = GLOBAL_CACHE.Player.GetXY()
            ally_array = ally_array = Routines.Agents.GetFilteredMinionArray(player_pos[0], player_pos[1], Conditions.MinionsInRangeArea)
            if len(ally_array) >= Conditions.MinionsInRange:
                number_of_features += 1
            else:
                number_of_features = 0
            

        #Py4GW.Console.Log("AreCastConditionsMet", f"feature count: {feature_count}, No of features {number_of_features}", Py4GW.Console.MessageType.Info)
        
        if feature_count == number_of_features:
            return True

        return False


    def SpiritBuffExists(self, skill_id):
        spirit_array = GLOBAL_CACHE.AgentArray.GetSpiritPetArray()
        distance = Range.Earshot.value
        spirit_array = AgentArray.Filter.ByDistance(spirit_array, GLOBAL_CACHE.Player.GetXY(), distance)
        spirit_array = AgentArray.Filter.ByCondition(spirit_array, lambda agent_id: GLOBAL_CACHE.Agent.IsAlive(agent_id))

        for spirit_id in spirit_array:
            model_value = GLOBAL_CACHE.Agent.GetPlayerNumber(spirit_id)

            # Check if model_value is valid for SpiritModelID Enum
            if model_value in SpiritModelID._value2member_map_:
                spirit_model_id = SpiritModelID(model_value)
                if SPIRIT_BUFF_MAP.get(spirit_model_id) == skill_id:
                    return True


        return False



    def IsReadyToCast(self, slot):
        # Check if the player is already casting
         # Validate target
        v_target = self.GetAppropiateTarget(slot)

        if v_target is None or v_target == 0:
            self.in_casting_routine = False
            return False, 0

        if GLOBAL_CACHE.Agent.IsCasting(GLOBAL_CACHE.Player.GetAgentID()):
            self.in_casting_routine = False
            return False, v_target
        #if GLOBAL_CACHE.Agent.GetCastingSkill(GLOBAL_CACHE.Player.GetAgentID()) != 0:
        #    self.in_casting_routine = False
        #    return False, v_target
        if GLOBAL_CACHE.SkillBar.GetCasting() != 0:
            self.in_casting_routine = False
            return False, v_target
        # Check if no skill is assigned to the slot
        if self.skills[slot].skill_id == 0:
            self.in_casting_routine = False
            return False, v_target
        # Check if the skill is recharging

        if not Routines.Checks.Skills.IsSkillIDReady(self.skills[slot].skill_id):
            self.in_casting_routine = False
            return False, v_target
        
        # Check if there is enough energy
        current_energy = self.GetEnergyValues(GLOBAL_CACHE.Player.GetAgentID()) * GLOBAL_CACHE.Agent.GetMaxEnergy(GLOBAL_CACHE.Player.GetAgentID())
        energy_cost = Routines.Checks.Skills.GetEnergyCostWithEffects(self.skills[slot].skill_id,GLOBAL_CACHE.Player.GetAgentID())
          
        if self.expertise_exists:
            energy_cost = Routines.Checks.Skills.apply_expertise_reduction(energy_cost, self.expertise_level, self.skills[slot].skill_id)
        
        if current_energy < energy_cost:
            self.in_casting_routine = False
            return False, v_target
        # Check if there is enough health
        current_hp = GLOBAL_CACHE.Agent.GetHealth(GLOBAL_CACHE.Player.GetAgentID())
        target_hp = self.skills[slot].custom_skill_data.Conditions.SacrificeHealth
        health_cost = GLOBAL_CACHE.Skill.Data.GetHealthCost(self.skills[slot].skill_id)
        if (current_hp < target_hp) and health_cost > 0:
            self.in_casting_routine = False
            return False, v_target
     
        # Check if there is enough adrenaline
        adrenaline_required = GLOBAL_CACHE.Skill.Data.GetAdrenaline(self.skills[slot].skill_id)
        if adrenaline_required > 0 and self.skills[slot].skillbar_data.adrenaline_a < adrenaline_required:
            self.in_casting_routine = False
            return False, v_target

        """
        # Check overcast conditions
        current_overcast = Agent.GetOvercast(Player.GetAgentID())
        overcast_target = self.skills[slot].custom_skill_data.Conditions.Overcast
        skill_overcast = Skill.Data.GetOvercast(self.skills[slot].skill_id)
        if (current_overcast >= overcast_target) and (skill_overcast > 0):
            self.in_casting_routine = False
            return False, 0
        """
                
        # Check combo conditions
        combo_type = GLOBAL_CACHE.Skill.Data.GetCombo(self.skills[slot].skill_id)
        dagger_status = GLOBAL_CACHE.Agent.GetDaggerStatus(v_target)
        if ((combo_type == 1 and dagger_status not in (0, 3)) or
            (combo_type == 2 and dagger_status != 1) or
            (combo_type == 3 and dagger_status != 2)):
            self.in_casting_routine = False
            return False, v_target
        
        # Check if the skill has the required conditions
        if not self.AreCastConditionsMet(slot, v_target):
            self.in_casting_routine = False
            return False, v_target
        
        if self.SpiritBuffExists(self.skills[slot].skill_id):
            self.in_casting_routine = False
            return False, v_target

        if self.HasEffect(v_target,self.skills[slot].skill_id):
            self.in_casting_routine = False
            return False, v_target
        
        return True, v_target

    def IsOOCSkill(self, slot):
        if self.skills[slot].custom_skill_data.Conditions.IsOutOfCombat:
            return True

        skill_type = self.skills[slot].custom_skill_data.SkillType
        skill_nature = self.skills[slot].custom_skill_data.Nature

        if(skill_type == SkillType.Form.value or
           skill_type == SkillType.Preparation.value or
           skill_nature == SkillNature.Healing.value or
           skill_nature == SkillNature.Hex_Removal.value or
           skill_nature == SkillNature.Condi_Cleanse.value or
           skill_nature == SkillNature.EnergyBuff.value or
           skill_nature == SkillNature.Resurrection.value
        ):
            return True

        return False

    def ChooseTarget(self, interact=True):       
        if not self.is_targeting_enabled:
            return False

        if not self.in_aggro:
            return False

            
        called_target = self.GetPartyTarget()
        #if GLOBAL_CACHE.Agent.IsAlive(called_target):
        if called_target != 0:
            self.SafeInteract(called_target)
            return True
            
        nearest = Routines.Agents.GetNearestEnemy(self.get_combat_distance())
        if nearest != 0:
            self.SafeInteract(nearest)
            return True
        
        
        
    def GetWeaponAttackAftercast(self):
        """
        Returns the attack speed of the current weapon.
        """
        weapon_type,_ = GLOBAL_CACHE.Agent.GetWeaponType(GLOBAL_CACHE.Player.GetAgentID())
        player = GLOBAL_CACHE.Agent.GetAgentByID(GLOBAL_CACHE.Player.GetAgentID())
        if player is None:
            return 0
        
        attack_speed = player.living_agent.weapon_attack_speed
        attack_speed_modifier = player.living_agent.attack_speed_modifier if player.living_agent.attack_speed_modifier != 0 else 1.0
        
        if attack_speed == 0:
            match weapon_type:
                case Weapon.Bow.value:
                    attack_speed = 2.475
                case Weapon.Axe.value:
                    attack_speed = 1.33
                case Weapon.Hammer.value:
                    attack_speed = 1.75
                case Weapon.Daggers.value:
                    attack_speed = 1.33
                case Weapon.Scythe.value:
                    attack_speed = 1.5
                case Weapon.Spear.value:
                    attack_speed = 1.5
                case Weapon.Sword.value:
                    attack_speed = 1.33
                case Weapon.Scepter.value:
                    attack_speed = 1.75
                case Weapon.Scepter2.value:
                    attack_speed = 1.75
                case Weapon.Wand.value:
                    attack_speed = 1.75
                case Weapon.Staff1.value:
                    attack_speed = 1.75
                case Weapon.Staff.value:
                    attack_speed = 1.75
                case Weapon.Staff2.value:
                    attack_speed = 1.75
                case Weapon.Staff3.value:
                    attack_speed = 1.75
                case _:
                    attack_speed = 1.75
                    
        return int((attack_speed / attack_speed_modifier) * 1000)

    def HandleCombat(self,ooc=False):
        """
        tries to Execute the next skill in the skill order.
        """
       
        slot = self.skill_pointer
        skill_id = self.skills[slot].skill_id
        
        is_skill_ready = self.IsSkillReady(slot)
            
        if not is_skill_ready:
            self.AdvanceSkillPointer()
            return False
        
        is_ooc_skill = self.IsOOCSkill(slot)

        if ooc and not is_ooc_skill:
            self.AdvanceSkillPointer()
            return False
         
         
        is_read_to_cast, target_agent_id = self.IsReadyToCast(slot)
 
        if not is_read_to_cast:
            self.AdvanceSkillPointer()
            return False
        

        if target_agent_id == 0:
            self.AdvanceSkillPointer()
            return False

        if not GLOBAL_CACHE.Agent.IsLiving(target_agent_id):
            return False
            
        self.in_casting_routine = True

        
        if self.fast_casting_exists:
            activation, recharge = Routines.Checks.Skills.apply_fast_casting(skill_id, self.fast_casting_level)
        else:
            activation = GLOBAL_CACHE.Skill.Data.GetActivation(skill_id)

        self.aftercast = activation * 1000
        self.aftercast += GLOBAL_CACHE.Skill.Data.GetAftercast(skill_id) * 1000 #750
        
        skill_type, _ = GLOBAL_CACHE.Skill.GetType(skill_id)
        if skill_type == SkillType.Attack.value:
            self.aftercast += self.GetWeaponAttackAftercast()
            
            
        self.aftercast += self.ping_handler.GetCurrentPing()

        self.aftercast_timer.Reset()
        GLOBAL_CACHE.SkillBar.UseSkill(self.skill_order[self.skill_pointer]+1, target_agent_id)
        self.ResetSkillPointer()
        return True
