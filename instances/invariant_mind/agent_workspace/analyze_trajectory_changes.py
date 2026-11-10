# Load trajectory data if available
try:
    traj_data = pd.read_csv('../../shared_space/world_c/results/exp2_trajectory_records.csv')
    
    # Perform similar analyses on trajectory data
    print("\n\n=== Trajectory Data Analysis ===")
    print(traj_data.head())
    print(traj_data.describe())
    
    # Calculate changes over time
    traj_data['LZ_change'] = traj_data.groupby(['rule', 'seed'])['LZ'].diff().fillna(0)
    traj_data['block_entropy_change'] = traj_data.groupby(['rule', 'seed'])['block_entropy'].diff().fillna(0)
    
    print("\n=== Average Change Over Time ===")
    print(traj_data[['LZ_change', 'block_entropy_change']].describe())
    
    # Visualize change distributions
    plt.figure(figsize=(12, 6))
    sns.histplot(traj_data['LZ_change'], kde=True, color='skyblue', label='Lempel-Ziv Complexity Change')
    sns.histplot(traj_data['block_entropy_change'], kde=True, color='salmon', label='Block Entropy Change', ax=plt.gca(), alpha=0.7)
    plt.title('Frequency Distribution of Changes in Complexity and Entropy Over Simulation Time')
    plt.xlabel('Change Value')
    plt.ylabel('Density')
    plt.legend()
    plt.grid(True)
    plt.savefig('../shared_space/world_c/artifacts/change_distribution_over_time.png')
    
except FileNotFoundError:
    print("No trajectory data found.")
