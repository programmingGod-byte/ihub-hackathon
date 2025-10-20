import React, {useState} from 'react';
import {
  View,
  Text,
  StyleSheet,
  SafeAreaView,
  ScrollView,
  TouchableOpacity,
  Image,
} from 'react-native';
import Icon from 'react-native-vector-icons/MaterialIcons';
import LinearGradient from 'react-native-linear-gradient';
import * as Animatable from 'react-native-animatable';

const ProfileScreen = () => {
  const [userInfo] = useState({
    name: 'Shivam Kumar',
    email: 'testuser@example.com',
    memberSince: 'January 2024',
    totalTrips: 47,
    ecoScore: 85,
    avatar: 'https://via.placeholder.com/100',
  });

  const [savedRoutes] = useState([
    {
      id: 1,
      title: 'Delhi to Mandi Green Route',
      description: 'Scenic route through national parks',
      distance: '320 km',
      duration: '6h 30m',
      ecoRating: 4.8,
      lastUsed: '2 days ago',
    },
    {
      id: 2,
      title: 'Mumbai to Goa Coastal Drive',
      description: 'Beautiful coastal highway journey',
      distance: '580 km',
      duration: '8h 15m',
      ecoRating: 4.6,
      lastUsed: '1 week ago',
    },
    {
      id: 3,
      title: 'Bangalore to Ooty Hill Station',
      description: 'Mountain route with tea plantations',
      distance: '280 km',
      duration: '5h 45m',
      ecoRating: 4.9,
      lastUsed: '2 weeks ago',
    },
  ]);

  const [achievements] = useState([
    {
      title: 'Eco Warrior',
      description: 'Completed 20 eco-friendly trips',
      icon: 'eco',
      color: '#4CAF50',
      unlocked: true,
    },
    {
      title: 'Green Explorer',
      description: 'Visited 10 national parks',
      icon: 'park',
      color: '#2E7D32',
      unlocked: true,
    },
    {
      title: 'Carbon Neutral',
      description: 'Offset 100kg CO2 emissions',
      icon: 'cloud-done',
      color: '#2196F3',
      unlocked: false,
    },
  ]);

  const renderUserInfo = () => (
    <Animatable.View animation="fadeInDown" style={styles.userCard}>
      <LinearGradient
        colors={['#2E7D32', '#4CAF50']}
        style={styles.userGradient}>
        <View style={styles.avatarContainer}>
          <View style={styles.avatar}>
            <Icon name="person" size={40} color="#FFFFFF" />
          </View>
        </View>
        <Text style={styles.userName}>{userInfo.name}</Text>
        <Text style={styles.userEmail}>{userInfo.email}</Text>
        <View style={styles.statsContainer}>
          <View style={styles.statItem}>
            <Text style={styles.statNumber}>{userInfo.totalTrips}</Text>
            <Text style={styles.statLabel}>Trips</Text>
          </View>
          <View style={styles.statItem}>
            <Text style={styles.statNumber}>{userInfo.ecoScore}</Text>
            <Text style={styles.statLabel}>Eco Score</Text>
          </View>
          <View style={styles.statItem}>
            <Text style={styles.statNumber}>4.8</Text>
            <Text style={styles.statLabel}>Rating</Text>
          </View>
        </View>
      </LinearGradient>
    </Animatable.View>
  );

  const renderSavedRoutes = () => (
    <Animatable.View animation="fadeInUp" style={styles.section}>
      <View style={styles.sectionHeader}>
        <Text style={styles.sectionTitle}>Saved Routes</Text>
        <TouchableOpacity>
          <Text style={styles.seeAllText}>See All</Text>
        </TouchableOpacity>
      </View>
      {savedRoutes.map((route, index) => (
        <Animatable.View
          key={route.id}
          animation="fadeInRight"
          delay={index * 100}
          style={styles.routeCard}>
          <View style={styles.routeHeader}>
            <View style={styles.routeInfo}>
              <Text style={styles.routeTitle}>{route.title}</Text>
              <Text style={styles.routeDescription}>{route.description}</Text>
            </View>
            <TouchableOpacity style={styles.routeMenu}>
              <Icon name="more-vert" size={20} color="#666" />
            </TouchableOpacity>
          </View>
          <View style={styles.routeDetails}>
            <View style={styles.routeDetailItem}>
              <Icon name="straighten" size={16} color="#666" />
              <Text style={styles.routeDetailText}>{route.distance}</Text>
            </View>
            <View style={styles.routeDetailItem}>
              <Icon name="schedule" size={16} color="#666" />
              <Text style={styles.routeDetailText}>{route.duration}</Text>
            </View>
            <View style={styles.routeDetailItem}>
              <Icon name="star" size={16} color="#FF9800" />
              <Text style={styles.routeDetailText}>{route.ecoRating}</Text>
            </View>
          </View>
          <View style={styles.routeFooter}>
            <Text style={styles.lastUsedText}>Last used: {route.lastUsed}</Text>
            <TouchableOpacity style={styles.useRouteButton}>
              <Text style={styles.useRouteButtonText}>Use Route</Text>
            </TouchableOpacity>
          </View>
        </Animatable.View>
      ))}
    </Animatable.View>
  );

  const renderAchievements = () => (
    <Animatable.View animation="fadeInUp" delay={200} style={styles.section}>
      <Text style={styles.sectionTitle}>Achievements</Text>
      <View style={styles.achievementsContainer}>
        {achievements.map((achievement, index) => (
          <Animatable.View
            key={index}
            animation="fadeInLeft"
            delay={300 + index * 100}
            style={[
              styles.achievementCard,
              !achievement.unlocked && styles.achievementLocked,
            ]}>
            <View style={[styles.achievementIcon, {backgroundColor: achievement.color}]}>
              <Icon
                name={achievement.icon}
                size={24}
                color={achievement.unlocked ? '#FFFFFF' : '#999'}
              />
            </View>
            <View style={styles.achievementInfo}>
              <Text
                style={[
                  styles.achievementTitle,
                  !achievement.unlocked && styles.achievementTitleLocked,
                ]}>
                {achievement.title}
              </Text>
              <Text
                style={[
                  styles.achievementDescription,
                  !achievement.unlocked && styles.achievementDescriptionLocked,
                ]}>
                {achievement.description}
              </Text>
            </View>
            {achievement.unlocked ? (
              <Icon name="check-circle" size={24} color="#4CAF50" />
            ) : (
              <Icon name="lock" size={24} color="#999" />
            )}
          </Animatable.View>
        ))}
      </View>
    </Animatable.View>
  );

  const renderQuickActions = () => (
    <Animatable.View animation="fadeInUp" delay={400} style={styles.section}>
      <Text style={styles.sectionTitle}>Quick Actions</Text>
      <View style={styles.actionsContainer}>
        <TouchableOpacity style={styles.actionButton}>
          <Icon name="add" size={24} color="#2E7D32" />
          <Text style={styles.actionButtonText}>New Route</Text>
        </TouchableOpacity>
        <TouchableOpacity style={styles.actionButton}>
          <Icon name="share" size={24} color="#2E7D32" />
          <Text style={styles.actionButtonText}>Share Profile</Text>
        </TouchableOpacity>
        <TouchableOpacity style={styles.actionButton}>
          <Icon name="settings" size={24} color="#2E7D32" />
          <Text style={styles.actionButtonText}>Settings</Text>
        </TouchableOpacity>
      </View>
    </Animatable.View>
  );

  return (
    <SafeAreaView style={styles.container}>
      <LinearGradient
        colors={['#E8F5E8', '#F0F8F0']}
        style={styles.gradient}>
        <ScrollView style={styles.content} showsVerticalScrollIndicator={false}>
          {renderUserInfo()}
          {renderSavedRoutes()}
          {renderAchievements()}
          {renderQuickActions()}
        </ScrollView>
      </LinearGradient>
    </SafeAreaView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
  },
  gradient: {
    flex: 1,
  },
  content: {
    flex: 1,
    paddingHorizontal: 20,
  },
  userCard: {
    marginTop: 20,
    marginBottom: 20,
    borderRadius: 20,
    overflow: 'hidden',
    shadowColor: '#000',
    shadowOffset: {width: 0, height: 4},
    shadowOpacity: 0.1,
    shadowRadius: 8,
    elevation: 8,
  },
  userGradient: {
    padding: 30,
    alignItems: 'center',
  },
  avatarContainer: {
    marginBottom: 15,
  },
  avatar: {
    width: 80,
    height: 80,
    borderRadius: 40,
    backgroundColor: 'rgba(255, 255, 255, 0.2)',
    justifyContent: 'center',
    alignItems: 'center',
  },
  userName: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#FFFFFF',
    marginBottom: 5,
  },
  userEmail: {
    fontSize: 16,
    color: 'rgba(255, 255, 255, 0.8)',
    marginBottom: 20,
  },
  statsContainer: {
    flexDirection: 'row',
    justifyContent: 'space-around',
    width: '100%',
  },
  statItem: {
    alignItems: 'center',
  },
  statNumber: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#FFFFFF',
  },
  statLabel: {
    fontSize: 14,
    color: 'rgba(255, 255, 255, 0.8)',
    marginTop: 5,
  },
  section: {
    marginBottom: 30,
  },
  sectionHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 15,
  },
  sectionTitle: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#2E7D32',
  },
  seeAllText: {
    fontSize: 16,
    color: '#2E7D32',
    fontWeight: '500',
  },
  routeCard: {
    backgroundColor: '#FFFFFF',
    borderRadius: 15,
    padding: 20,
    marginBottom: 15,
    shadowColor: '#000',
    shadowOffset: {width: 0, height: 2},
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 4,
  },
  routeHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'flex-start',
    marginBottom: 15,
  },
  routeInfo: {
    flex: 1,
  },
  routeTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 5,
  },
  routeDescription: {
    fontSize: 14,
    color: '#666',
  },
  routeMenu: {
    padding: 5,
  },
  routeDetails: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: 15,
  },
  routeDetailItem: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  routeDetailText: {
    fontSize: 14,
    color: '#666',
    marginLeft: 5,
  },
  routeFooter: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  lastUsedText: {
    fontSize: 12,
    color: '#999',
  },
  useRouteButton: {
    backgroundColor: '#2E7D32',
    borderRadius: 20,
    paddingHorizontal: 20,
    paddingVertical: 8,
  },
  useRouteButtonText: {
    color: '#FFFFFF',
    fontSize: 14,
    fontWeight: 'bold',
  },
  achievementsContainer: {
    gap: 15,
  },
  achievementCard: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#FFFFFF',
    borderRadius: 15,
    padding: 20,
    shadowColor: '#000',
    shadowOffset: {width: 0, height: 2},
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 4,
  },
  achievementLocked: {
    opacity: 0.6,
  },
  achievementIcon: {
    width: 50,
    height: 50,
    borderRadius: 25,
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: 15,
  },
  achievementInfo: {
    flex: 1,
  },
  achievementTitle: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 5,
  },
  achievementTitleLocked: {
    color: '#999',
  },
  achievementDescription: {
    fontSize: 14,
    color: '#666',
  },
  achievementDescriptionLocked: {
    color: '#CCC',
  },
  actionsContainer: {
    flexDirection: 'row',
    justifyContent: 'space-between',
  },
  actionButton: {
    flex: 1,
    backgroundColor: '#FFFFFF',
    borderRadius: 15,
    padding: 20,
    alignItems: 'center',
    marginHorizontal: 5,
    shadowColor: '#000',
    shadowOffset: {width: 0, height: 2},
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 4,
  },
  actionButtonText: {
    fontSize: 14,
    color: '#2E7D32',
    fontWeight: 'bold',
    marginTop: 8,
  },
});

export default ProfileScreen;
