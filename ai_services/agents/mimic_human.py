import time
import random
import numpy as np
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum
import json


class Activity(Enum):
    """Enum for available activities"""
    RESTING = "resting"
    WALKING = "walking"
    RUNNING = "running"
    EXERCISING = "exercising"
    SLEEPING = "sleeping"
    STRESSED = "stressed"
    MEDITATION = "meditation"


@dataclass
class UserProfile:
    """User profile for personalized data generation"""
    user_id: str = "USER001"
    age: int = 30
    gender: str = "M"
    weight_kg: float = 70.0
    height_cm: float = 170.0
    fitness_level: str = "average"  # low, average, high


class RealTimeWearableData:
    """
    Real-time wearable data generator that returns JSON data on demand.
    No file I/O, pure function-based data generation for immediate use.
    """
    
    def __init__(self, user_profile: UserProfile = None):
        if user_profile is None:
            user_profile = UserProfile()
        self.user_profile = user_profile
        self.start_time = datetime.now()
        self.current_activity = Activity.RESTING.value
        
        # Current physiological state for smooth transitions
        self.current_state = self._initialize_state()
        self.total_steps = 0
        self.total_calories = 0.0
        
        # Activity-specific physiological ranges
        self.activity_profiles = self._setup_activity_profiles()
    
    def _initialize_state(self) -> Dict[str, float]:
        """Initialize baseline physiological state"""
        age_adjustment = max(0, (self.user_profile.age - 30) * 0.3)
        gender_hr_adjust = -3 if self.user_profile.gender == "F" else 2
        
        return {
            'heart_rate': 72 + gender_hr_adjust - age_adjustment,
            'steps': 0,
            'calories': 0.0,
            'blood_oxygen': 98.5,
            'temperature': 36.7,
            'stress_level': 25.0,
            'sleep_quality': 85.0,
            'systolic_bp': 118 + (self.user_profile.age * 0.2),
            'diastolic_bp': 78,
            'respiratory_rate': 15.5,
            'hrv': 45.0,  # Heart Rate Variability
            'recovery_rate': 0.8
        }
    
    def _setup_activity_profiles(self) -> Dict[str, Dict]:
        """Setup realistic physiological ranges for each activity"""
        bmr_per_second = self._calculate_bmr() / 86400
        
        return {
            Activity.RESTING.value: {
                'heart_rate': (58, 76),
                'steps_per_second': 0,
                'calories_per_second': bmr_per_second * 1.1,
                'stress_range': (15, 35),
                'temperature_range': (36.3, 36.8),
                'respiratory_range': (12, 16),
                'blood_pressure': ((108, 122), (68, 82)),
                'blood_oxygen_range': (97.5, 100),
                'hrv_range': (40, 60)
            },
            Activity.WALKING.value: {
                'heart_rate': (88, 112),
                'steps_per_second': 1.8,
                'calories_per_second': bmr_per_second * 3.5,
                'stress_range': (22, 42),
                'temperature_range': (36.6, 37.1),
                'respiratory_range': (16, 22),
                'blood_pressure': ((112, 128), (72, 86)),
                'blood_oxygen_range': (96.5, 99.5),
                'hrv_range': (35, 55)
            },
            Activity.RUNNING.value: {
                'heart_rate': (135, 175),
                'steps_per_second': 4.2,
                'calories_per_second': bmr_per_second * 8.5,
                'stress_range': (45, 75),
                'temperature_range': (36.9, 37.6),
                'respiratory_range': (28, 48),
                'blood_pressure': ((125, 155), (78, 98)),
                'blood_oxygen_range': (94.5, 98.5),
                'hrv_range': (25, 45)
            },
            Activity.EXERCISING.value: {
                'heart_rate': (125, 165),
                'steps_per_second': 2.8,
                'calories_per_second': bmr_per_second * 7.0,
                'stress_range': (55, 85),
                'temperature_range': (37.0, 37.7),
                'respiratory_range': (24, 42),
                'blood_pressure': ((120, 145), (75, 92)),
                'blood_oxygen_range': (95.5, 99),
                'hrv_range': (30, 50)
            },
            Activity.SLEEPING.value: {
                'heart_rate': (48, 62),
                'steps_per_second': 0,
                'calories_per_second': bmr_per_second * 0.95,
                'stress_range': (8, 22),
                'temperature_range': (36.1, 36.4),
                'respiratory_range': (9, 13),
                'blood_pressure': ((102, 115), (62, 72)),
                'blood_oxygen_range': (98, 100),
                'hrv_range': (50, 70)
            },
            Activity.STRESSED.value: {
                'heart_rate': (82, 108),
                'steps_per_second': 0.3,
                'calories_per_second': bmr_per_second * 2.2,
                'stress_range': (65, 95),
                'temperature_range': (36.7, 37.3),
                'respiratory_range': (18, 26),
                'blood_pressure': ((122, 142), (80, 95)),
                'blood_oxygen_range': (97, 99.5),
                'hrv_range': (20, 40)
            },
            Activity.MEDITATION.value: {
                'heart_rate': (52, 68),
                'steps_per_second': 0,
                'calories_per_second': bmr_per_second * 1.05,
                'stress_range': (3, 18),
                'temperature_range': (36.2, 36.5),
                'respiratory_range': (7, 11),
                'blood_pressure': ((105, 118), (65, 75)),
                'blood_oxygen_range': (98.5, 100),
                'hrv_range': (55, 75)
            }
        }
    
    def _calculate_bmr(self) -> float:
        """Calculate Basal Metabolic Rate using Harris-Benedict equation"""
        if self.user_profile.gender.upper() == "M":
            bmr = 88.362 + (13.397 * self.user_profile.weight_kg) + \
                  (4.799 * self.user_profile.height_cm) - (5.677 * self.user_profile.age)
        else:
            bmr = 447.593 + (9.247 * self.user_profile.weight_kg) + \
                  (3.098 * self.user_profile.height_cm) - (4.330 * self.user_profile.age)
        return bmr
    
    def _generate_smooth_transition(self, current: float, target: float, 
                                  variance: float, smoothness: float = 0.15) -> float:
        """Generate smooth, realistic physiological transitions"""
        if current is None:
            return target
        
        diff = target - current
        change = diff * smoothness + random.uniform(-variance, variance)
        return max(0, current + change)
    
    def _apply_circadian_rhythm(self, base_value: float, metric: str) -> float:
        """Apply circadian rhythm patterns to metrics"""
        now = datetime.now()
        hour_of_day = now.hour + now.minute / 60.0
        
        if metric == 'heart_rate':
            # Lower at night, peaks in afternoon
            adjustment = -4 * np.cos((hour_of_day - 14) * np.pi / 12)
        elif metric == 'temperature':
            # Lowest at 4 AM, highest at 6 PM
            adjustment = 0.25 * np.cos((hour_of_day - 18) * np.pi / 12)
        elif metric == 'stress_level':
            # Higher during work hours (8 AM - 6 PM)
            adjustment = 8 * (0.5 + 0.5 * np.sin((hour_of_day - 14) * np.pi / 8))
        else:
            adjustment = 0
        
        return base_value + adjustment
    
    def _apply_personalization(self, value: float, metric: str, activity: str) -> float:
        """Apply age, gender, and fitness level adjustments"""
        adjustments = {
            'heart_rate': {
                Activity.RESTING.value: -0.25 * self.user_profile.age / 30,
                Activity.WALKING.value: -0.15 * self.user_profile.age / 30 - (5 if self.user_profile.fitness_level == "high" else 0),
                Activity.RUNNING.value: -0.1 * self.user_profile.age / 30 - (8 if self.user_profile.fitness_level == "high" else 0)
            },
            'systolic_bp': {
                Activity.RESTING.value: 0.4 * self.user_profile.age / 30,
                Activity.STRESSED.value: 0.6 * self.user_profile.age / 30,
                Activity.EXERCISING.value: 0.3 * self.user_profile.age / 30
            }
        }
        
        if metric in adjustments and activity in adjustments[metric]:
            adjustment = adjustments[metric][activity]
            return value + adjustment
        
        return value
    
    def generate_realtime_data(self, activity: str = None, 
                             duration_seconds: int = 1) -> Dict[str, Any]:
        """
        Generate real-time wearable data and return as JSON-compatible dict.
        
        Args:
            activity: Specific activity to simulate (defaults to current)
            duration_seconds: Time duration for this data point (affects steps/calories)
            
        Returns:
            Dictionary containing all physiological metrics with timestamp
        """
        if activity and activity in self.activity_profiles:
            self.current_activity = activity
        elif activity is None:
            activity = self.current_activity
        
        profile = self.activity_profiles[self.current_activity]
        timestamp = datetime.now().isoformat()
        
        # Generate physiological metrics with smooth transitions
        metrics = {}
        
        # Heart Rate with circadian and personalization adjustments
        target_hr = random.uniform(*profile['heart_rate'])
        target_hr = self._apply_circadian_rhythm(target_hr, 'heart_rate')
        target_hr = self._apply_personalization(target_hr, 'heart_rate', activity)
        
        metrics['heart_rate'] = round(
            self._generate_smooth_transition(
                self.current_state['heart_rate'], 
                target_hr, 
                variance=2.5
            )
        )
        
        # Heart Rate Variability (HRV) - higher when relaxed
        target_hrv = random.uniform(*profile['hrv_range'])
        if activity in [Activity.RESTING.value, Activity.MEDITATION.value, Activity.SLEEPING.value]:
            target_hrv += random.uniform(5, 15)
        else:
            target_hrv -= random.uniform(3, 8)
        
        metrics['hrv'] = round(
            self._generate_smooth_transition(
                self.current_state['hrv'], 
                target_hrv, 
                variance=3.0
            ), 1
        )
        
        # Steps (cumulative)
        steps_increment = profile['steps_per_second'] * duration_seconds
        self.total_steps += steps_increment + random.uniform(-0.5, 1.5)
        metrics['steps'] = int(max(0, self.total_steps))
        
        # Calories burned (cumulative)
        cal_increment = profile['calories_per_second'] * duration_seconds
        self.total_calories += cal_increment + random.uniform(-0.02, 0.05)
        metrics['calories'] = round(max(0, self.total_calories), 2)
        
        # Blood Oxygen with activity-specific drops during intense exercise
        target_o2 = random.uniform(*profile['blood_oxygen_range'])
        if activity == Activity.RUNNING.value:
            target_o2 -= random.uniform(0.5, 2.0)
        elif activity in [Activity.EXERCISING.value, Activity.WALKING.value]:
            target_o2 -= random.uniform(0.2, 1.0)
        
        metrics['blood_oxygen'] = round(
            np.clip(
                self._generate_smooth_transition(
                    self.current_state['blood_oxygen'], 
                    target_o2, 
                    variance=0.4
                ), 
                94, 100
            ), 1
        )
        
        # Body Temperature with circadian rhythm
        target_temp = random.uniform(*profile['temperature_range'])
        target_temp = self._apply_circadian_rhythm(target_temp, 'temperature')
        
        metrics['temperature'] = round(
            self._generate_smooth_transition(
                self.current_state['temperature'], 
                target_temp, 
                variance=0.08
            ), 2
        )
        
        # Stress Level with circadian influence
        target_stress = random.uniform(*profile['stress_range'])
        target_stress = self._apply_circadian_rhythm(target_stress, 'stress_level')
        
        # Stress increases with exercise intensity, decreases with meditation
        if activity in [Activity.RUNNING.value, Activity.EXERCISING.value]:
            target_stress += random.uniform(8, 20)
        elif activity == Activity.MEDITATION.value:
            target_stress -= random.uniform(10, 25)
        
        metrics['stress_level'] = round(
            np.clip(
                self._generate_smooth_transition(
                    self.current_state['stress_level'], 
                    target_stress, 
                    variance=4.0
                ), 
                0, 100
            )
        )
        
        # Sleep Quality (only meaningful during sleep, otherwise shows readiness)
        if activity == Activity.SLEEPING.value:
            sleep_improvement = random.uniform(0.4, 1.2)
            sleep_value = min(100, self.current_state['sleep_quality'] + sleep_improvement)
        else:
            sleep_decay = random.uniform(-0.2, -0.05)
            sleep_value = max(50, self.current_state['sleep_quality'] + sleep_decay)
            # Convert to sleep readiness score when awake
            sleep_value = min(100, sleep_value + (100 - metrics['stress_level']) * 0.3)
        
        metrics['sleep_quality'] = round(np.clip(sleep_value, 0, 100), 1)
        
        # Blood Pressure with age adjustments
        sys_range, dia_range = profile['blood_pressure']
        target_sys = random.uniform(*sys_range)
        target_dia = random.uniform(*dia_range)
        target_sys = self._apply_personalization(target_sys, 'systolic_bp', activity)
        
        metrics['systolic_bp'] = round(
            self._generate_smooth_transition(
                self.current_state['systolic_bp'], 
                target_sys, 
                variance=1.8
            )
        )
        metrics['diastolic_bp'] = round(
            self._generate_smooth_transition(
                self.current_state['diastolic_bp'], 
                target_dia, 
                variance=1.5
            )
        )
        
        # Respiratory Rate
        target_rr = random.uniform(*profile['respiratory_range'])
        if activity == Activity.RUNNING.value:
            target_rr += random.uniform(5, 15)
        elif activity == Activity.MEDITATION.value:
            target_rr -= random.uniform(2, 4)
        
        metrics['respiratory_rate'] = round(
            self._generate_smooth_transition(
                self.current_state['respiratory_rate'], 
                target_rr, 
                variance=1.2
            )
        )
        
        # Recovery Rate (improves during rest/meditation, drops during stress/exercise)
        if activity in [Activity.RESTING.value, Activity.MEDITATION.value, Activity.SLEEPING.value]:
            recovery_change = random.uniform(0.05, 0.15)
        else:
            recovery_change = random.uniform(-0.08, -0.02)
        
        metrics['recovery_rate'] = round(
            np.clip(
                self.current_state['recovery_rate'] + recovery_change, 
                0, 1
            ), 2
        )
        
        # Calculate exertion level based on heart rate relative to max HR
        max_hr_estimate = 220 - self.user_profile.age
        exertion_percentage = (metrics['heart_rate'] / max_hr_estimate) * 100
        metrics['exertion_level'] = round(np.clip(exertion_percentage, 0, 100), 1)
        
        # VO2 Max estimate (simplified)
        if activity in [Activity.RUNNING.value, Activity.EXERCISING.value]:
            vo2_estimate = 35 + (metrics['heart_rate'] - 70) * 0.1
            if self.user_profile.fitness_level == "high":
                vo2_estimate += 8
            elif self.user_profile.fitness_level == "low":
                vo2_estimate -= 5
        else:
            vo2_estimate = 30 + random.uniform(-3, 3)
        
        metrics['vo2_max_estimate'] = round(vo2_estimate, 1)
        
        # Energy level (inverse relationship with stress and exertion)
        energy_base = 100 - metrics['stress_level'] * 0.8
        energy_base -= metrics['exertion_level'] * 0.3
        if activity in [Activity.SLEEPING.value, Activity.MEDITATION.value]:
            energy_base += 15
        metrics['energy_level'] = round(np.clip(energy_base + random.uniform(-10, 10), 0, 100))
        
        # Create final data structure
        realtime_data = {
            "timestamp": timestamp,
            "user_id": self.user_profile.user_id,
            "age": self.user_profile.age,
            "gender": self.user_profile.gender,
            "current_activity": self.current_activity,
            "duration_seconds": duration_seconds,
            "physiological_metrics": metrics,
            "bmr_kcal_day": round(self._calculate_bmr(), 1),
            "fitness_level": self.user_profile.fitness_level,
            "session_totals": {
                "total_steps": metrics['steps'],
                "total_calories": metrics['calories']
            },
            "health_indicators": {
                "recovery_score": self._calculate_recovery_score(metrics,activity),
                "cardio_fitness": self._calculate_cardio_fitness(metrics),
                "stress_recovery_balance": round((metrics['recovery_rate'] * 100) - (metrics['stress_level'] * 0.5), 1)
            }
        }
        
        # Update state for next call
        self.current_state.update({
            'heart_rate': metrics['heart_rate'],
            'hrv': metrics['hrv'],
            'blood_oxygen': metrics['blood_oxygen'],
            'temperature': metrics['temperature'],
            'stress_level': metrics['stress_level'],
            'sleep_quality': metrics['sleep_quality'],
            'systolic_bp': metrics['systolic_bp'],
            'diastolic_bp': metrics['diastolic_bp'],
            'respiratory_rate': metrics['respiratory_rate'],
            'recovery_rate': metrics['recovery_rate']
        })
        
        return realtime_data
    
    def _calculate_recovery_score(self, metrics: Dict, activity: str) -> int:
        score = 50
        score += min(25, metrics['sleep_quality'] * 0.3)
        score += min(20, metrics['hrv'] * 0.4)
        score -= min(15, metrics['stress_level'] * 0.2)
        score += min(10, metrics['recovery_rate'] * 50)

        if activity in [Activity.SLEEPING.value, Activity.MEDITATION.value]:
            score += 10

        return round(np.clip(score, 0, 100))

    
    def _calculate_cardio_fitness(self, metrics: Dict) -> str:
        """Calculate cardio fitness level based on current metrics"""
        vo2 = metrics['vo2_max_estimate']
        hrv = metrics['hrv']
        recovery = metrics['recovery_rate']
        
        if vo2 >= 45 and hrv >= 50 and recovery >= 0.7:
            return "excellent"
        elif vo2 >= 38 and hrv >= 40 and recovery >= 0.6:
            return "good"
        elif vo2 >= 32 and hrv >= 30 and recovery >= 0.5:
            return "average"
        else:
            return "below_average"
    
    def set_activity(self, activity: str) -> None:
        """Set current activity for subsequent data generation"""
        if activity in self.activity_profiles:
            self.current_activity = activity
        else:
            available = list(self.activity_profiles.keys())
            print(f"⚠️  Unknown activity '{activity}'. Available: {available}")
    
    def set_user_profile(self, user_profile: UserProfile) -> None:
        """Update user profile and reset physiological state"""
        self.user_profile = user_profile
        self.current_state = self._initialize_state()
        self.total_steps = 0
        self.total_calories = 0.0
        self.current_activity = Activity.RESTING.value
        self.start_time = datetime.now()
    
    def get_current_status(self) -> Dict[str, Any]:
        """Get current status without generating new data"""
        elapsed = (datetime.now() - self.start_time).total_seconds()
        return {
            "user_id": self.user_profile.user_id,
            "current_activity": self.current_activity,
            "session_duration_seconds": round(elapsed),
            "total_steps": int(self.total_steps),
            "total_calories": round(self.total_calories, 2),
            "current_heart_rate": round(self.current_state['heart_rate']),
            "current_stress": round(self.current_state['stress_level']),
            "timestamp": datetime.now().isoformat()
        }


# High-level convenience functions for immediate JSON generation
def get_realtime_wearable_json(user_profile: UserProfile, 
                             activity: str, 
                             duration: int = 1,
                             generator: Optional[RealTimeWearableData] = None) -> str:
    """
    Generate real-time wearable data and return as JSON string.
    
    Args:
        user_profile: User demographic and fitness information
        activity: Current activity type
        duration: Duration in seconds for this data point
        generator: Existing generator instance (maintains state)
    
    Returns:
        JSON string containing complete physiological data
    """
    if generator is None:
        generator = RealTimeWearableData(user_profile)
        generator.set_activity(activity)
    else:
        generator.set_activity(activity)
    
    data = generator.generate_realtime_data(activity, duration)
    return json.dumps(data, indent=2)


def get_live_monitoring_json(user_profile: UserProfile, 
                           activity_sequence: List[str], 
                           duration_per_activity: int = 30) -> str:
    """
    Generate live monitoring data for an activity sequence.
    
    Args:
        user_profile: User profile
        activity_sequence: List of activities to cycle through
        duration_per_activity: Seconds per activity
    
    Returns:
        JSON string with batched real-time data
    """
    generator = RealTimeWearableData(user_profile)
    all_data = []
    
    for activity in activity_sequence:
        generator.set_activity(activity)
        data_point = generator.generate_realtime_data(activity, duration_per_activity)
        all_data.append(data_point)
        time.sleep(0.1)  # Small delay for realism
    
    monitoring_data = {
        "user_id": user_profile.user_id,
        "monitoring_type": "live_session",
        "start_time": generator.start_time.isoformat(),
        "data_points": all_data,
        "session_summary": {
            "total_duration": sum(dp["duration_seconds"] for dp in all_data),
            "activities_covered": list(dict.fromkeys([dp["current_activity"] for dp in all_data])),
            "avg_heart_rate": round(np.mean([dp["physiological_metrics"]["heart_rate"] for dp in all_data]), 1),
            "max_stress": max(dp["physiological_metrics"]["stress_level"] for dp in all_data),
            "total_calories": all_data[-1]["session_totals"]["total_calories"]
        }
    }
    
    return json.dumps(monitoring_data, indent=2)


def get_instant_health_snapshot(user_profile: UserProfile, 
                               current_activity: str) -> str:
    """
    Get an instant health snapshot for quick monitoring.
    
    Returns:
        Compact JSON with essential health metrics
    """
    generator = RealTimeWearableData(user_profile)
    data = generator.generate_realtime_data(current_activity, duration_seconds=1)
    
    # Create compact snapshot
    snapshot = {
        "timestamp": data["timestamp"],
        "user_id": data["user_id"],
        "activity": data["current_activity"],
        "vital_signs": {
            "heart_rate": data["physiological_metrics"]["heart_rate"],
            "blood_pressure": f"{data['physiological_metrics']['systolic_bp']}/{data['physiological_metrics']['diastolic_bp']}",
            "blood_oxygen": data["physiological_metrics"]["blood_oxygen"],
            "temperature": data["physiological_metrics"]["temperature"],
            "respiratory_rate": data["physiological_metrics"]["respiratory_rate"]
        },
        "wellness_scores": {
            "stress_level": data["physiological_metrics"]["stress_level"],
            "energy_level": data["physiological_metrics"]["energy_level"],
            "recovery_score": data["health_indicators"]["recovery_score"],
            "cardio_fitness": data["health_indicators"]["cardio_fitness"]
        },
        "performance_metrics": {
            "steps_today": data["session_totals"]["total_steps"],
            "calories_burned": data["session_totals"]["total_calories"],
            "exertion_level": data["physiological_metrics"]["exertion_level"],
            "vo2_max": data["physiological_metrics"]["vo2_max_estimate"]
        }
    }
    
    return json.dumps(snapshot, indent=2)


# Example usage and testing
if __name__ == "__main__":
    print("="*80)
    print("REAL-TIME WEARABLE DATA GENERATOR")
    print("Pure JSON output - No file exports, instant data generation")
    print("="*80)
    
    # Create user profiles
    athlete = UserProfile(user_id="ATHLETE_001", age=28, gender="M", 
                         weight_kg=78, height_cm=182, fitness_level="high")
    office_worker = UserProfile(user_id="OFFICE_001", age=34, gender="F", 
                               weight_kg=62, height_cm=168, fitness_level="average")
    
    print(f"\n👤 Created profiles:")
    print(f"   - {athlete.user_id}: {athlete.age}yo {athlete.gender}, {athlete.fitness_level} fitness")
    print(f"   - {office_worker.user_id}: {office_worker.age}yo {office_worker.gender}, {office_worker.fitness_level} fitness")
    
    print("\n" + "="*60)
    print("DEMO 1: Single Real-Time Data Point")
    print("="*60)
    
    # Generate real-time data for athlete during running
    json_data = get_realtime_wearable_json(athlete, Activity.RUNNING.value, duration=5)
    print(json_data)
    
    print("\n" + "="*60)
    print("DEMO 2: Instant Health Snapshot")
    print("="*60)
    
    # Get quick health snapshot for office worker
    snapshot_json = get_instant_health_snapshot(office_worker, Activity.STRESSED.value)
    print(snapshot_json)
    
    print("\n" + "="*60)
    print("DEMO 3: Live Monitoring Session")
    print("="*60)
    
    # Simulate a workout monitoring session
    workout_sequence = [
        Activity.WALKING.value,
        Activity.RUNNING.value, 
        Activity.EXERCISING.value,
        Activity.RESTING.value
    ]
    
    monitoring_json = get_live_monitoring_json(
        athlete, 
        workout_sequence, 
        duration_per_activity=10  # 10 seconds per activity for demo
    )
    print(monitoring_json)
    
    print("\n" + "="*60)
    print("DEMO 4: Real-Time Integration Example")
    print("="*60)
    
    # Simulate real-time API integration
    generator = RealTimeWearableData(athlete)
    
    print("🕐 Simulating 6 seconds of real-time monitoring...")
    for i in range(6):
        # Change activity every few seconds
        if i == 2:
            current_activity = Activity.EXERCISING.value
        elif i == 4:
            current_activity = Activity.RESTING.value
        else:
            current_activity = Activity.RUNNING.value
        
        realtime_json = generator.generate_realtime_data(current_activity, duration_seconds=1)
        
        print(f"\n⏱️  [{i+1}s] Activity: {current_activity}")
        print(f"   💓 HR: {realtime_json['physiological_metrics']['heart_rate']}bpm")
        print(f"   📈 Stress: {realtime_json['physiological_metrics']['stress_level']}%")
        print(f"   🔥 Calories: {realtime_json['session_totals']['total_calories']:.1f}kcal")
        print(f"   🏃 Steps: {realtime_json['session_totals']['total_steps']:,}")
        print(f"   📊 Recovery: {realtime_json['health_indicators']['recovery_score']}/100")
        
        # In a real app, you'd send this JSON to your API/database
        # print(json.dumps(realtime_json))  # This is your API payload
    
    print("\n" + "="*60)
    print("✅ REAL-TIME JSON GENERATION COMPLETE")
    print("="*60)
    print("\n🚀 Usage Examples:")
    print("\n📱 For Mobile App Integration:")
    print('   data = get_realtime_wearable_json(user, "running", 1)')
    print('   # Send to your backend API')
    print('   requests.post("/api/vitals", json=data)')
    print("\n📊 For Dashboard Updates:")
    print('   snapshot = get_instant_health_snapshot(user, current_activity)')
    print('   # Update UI with json.loads(snapshot)')
    print("\n🔄 For Live Monitoring:")
    print('   generator = RealTimeWearableData(user)')
    print('   while monitoring:')
    print('       json_data = generator.generate_realtime_data(activity)')
    print('       # Process real-time data')
    print("\n💡 Features:")
    print("   • Instant JSON output - no file I/O")
    print("   • Real-time physiological state tracking")
    print("   • Personalized by age, gender, fitness level")
    print("   • Complete health indicators and performance metrics")
    print("   • Ready for API integration and live monitoring")
