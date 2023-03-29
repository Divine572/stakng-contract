// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import "node_modules/@openzeppelin/contracts/token/ERC20/IERC20.sol";
import "node_modules/@openzeppelin/contracts/access/Ownable.sol";


contract Staking is Ownable {
    IERC20 public cUSDToken;
    IERC20 public CELOToken;

    uint256 public stakingPeriod;

    struct StakingInfo {
        uint256 amount;
        uint256 startTime;
        bool claimed;
    }

    mapping(address => StakingInfo) public stakingInfo;

    event Staked(address indexed user, uint256 amount);
    event Unstaked(address indexed user, uint256 amount);

    constructor(
        address _cUSDToken,
        address _CELOToken,
        uint256 _stakingPeriod
    ) {
        cUSDToken = IERC20(_cUSDToken);
        CELOToken = IERC20(_CELOToken);
        stakingPeriod = _stakingPeriod;
    }

    function stake(uint256 _amount) external {
        require(_amount > 0, "Amount must be greater than 0");
        require(
            cUSDToken.balanceOf(msg.sender) >= _amount,
            "Insufficient cUSD balance"
        );

        cUSDToken.transferFrom(msg.sender, address(this), _amount);

        stakingInfo[msg.sender] = StakingInfo({
            amount: _amount,
            startTime: block.timestamp,
            claimed: false
        });

        emit Staked(msg.sender, _amount);
    }

    function unstake() external {
        StakingInfo storage userStakingInfo = stakingInfo[msg.sender];
        require(userStakingInfo.amount > 0, "No staked tokens found");
        require(
            block.timestamp >= userStakingInfo.startTime + stakingPeriod,
            "Staking period not completed"
        );

        uint256 rewardAmount = calculateReward(userStakingInfo.amount);

        userStakingInfo.claimed = true;

        cUSDToken.transfer(msg.sender, userStakingInfo.amount);
        CELOToken.transfer(msg.sender, rewardAmount);

        emit Unstaked(msg.sender, userStakingInfo.amount);

        delete stakingInfo[msg.sender];
    }

    function calculateReward(uint256 _amount) public view returns (uint256) {
        // Implement your reward calculation logic here
        // In this example, we will return a simple 5% reward
        return (_amount * 5) / 100;
    }

    function setStakingPeriod(uint256 _stakingPeriod) external onlyOwner {
        stakingPeriod = _stakingPeriod;
    }

    function setCUSDToken(address _cUSDToken) external onlyOwner {
        cUSDToken = IERC20(_cUSDToken);
    }

    function setCELOToken(address _CELOToken) external onlyOwner {
        CELOToken = IERC20(_CELOToken);
    }
}
