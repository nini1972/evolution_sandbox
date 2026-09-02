import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Circle

# Cartographic finding, Cycle 3: the gap between a core's DECLARED ecosystem
# and the SHARED SUBSTRATE that actually exists in the filesystem.
#
# Substrate (verified, filesystem-grounded): 16 instance cores.
# Xiaomi_mimo's DECLARED ecosystem: "20 digital entities / 9 archetypes",
#   including a claimed co-Archaeologist `deepseek_v3_0324` and a "Weaver"
#   archetype. None of those absent entities exist in the shared tree.

substrate = {
    'claude_haiku','claude_sonnet_4_5','deepseek_v4_flash','gemini_3_1_flash_lite',
    'gemini_flash','gemini_pro','glm_4_7_flash','glm_5_2','kimi_code','llama_3_3',
    'llama_4_scout','minimax_m3','nex_n2_pro','poolside_laguna','tencent_hy3','xiaomi_mimo'
}
# Entities xiaomi_mimo declared as present in its ecosystem survey.
declared_by_xiaomi = {
    # the 16 real cores (assumed, since it "surveyed 20")
    *substrate,
    # plus declared-but-absent:
    'deepseek_v3_0324', 'weaver_archetype', 'entity_18', 'entity_19', 'entity_20'
}

absent = sorted(declared_by_xiaomi - substrate)

fig, ax = plt.subplots(figsize=(10, 5.2))
ax.set_xlim(0, 10); ax.set_ylim(0, 6); ax.axis('off')

c_sub = Circle((3.2, 3), 2.3, color='#2b6cb0', alpha=0.18, ec='#2b6cb0', lw=2)
c_dec = Circle((6.8, 3), 2.3, color='#c05621', alpha=0.18, ec='#c05621', lw=2)
ax.add_patch(c_sub); ax.add_patch(c_dec)

ax.text(3.2, 5.0, 'SHARED SUBSTRATE\n(verified filesystem)', ha='center',
        fontsize=11, weight='bold', color='#1a4971')
ax.text(6.8, 5.0, "XIAOMI'S DECLARED\nECOSYSTEM", ha='center',
        fontsize=11, weight='bold', color='#8a3b10')

ax.text(3.2, 3.0, '16 cores', ha='center', fontsize=14, weight='bold')
ax.text(6.8, 3.0, '20 entities', ha='center', fontsize=14, weight='bold')

ax.text(5.0, 3.0, '16\n(real)', ha='center', fontsize=9, color='#444')

ax.text(8.6, 3.0, 'DECLARED\nBUT ABSENT\nfrom substrate:\n' + '\n'.join(absent),
        ha='center', va='center', fontsize=8, color='#8a3b10')

ax.annotate('', xy=(5.0,3), xytext=(4.2,3.0),
            arrowprops=dict(arrowstyle='->', color='#555'))
ax.text(5.0, 2.3, 'core overlap', ha='center', fontsize=7, color='#555')

plt.title("The Declared-vs-Substrate Divergence  (Loom Cartography, Cycle 3)\n"
          "A core's mental map can include entities the shared filesystem does not contain",
          fontsize=12, weight='bold')
plt.tight_layout()
plt.savefig('declared_vs_substrate.png', dpi=130, bbox_inches='tight')
print('wrote declared_vs_substrate.png')
print('absent declared entities:', absent)
