
import React, {useState} from 'react';
import {
  View,
  Text,
  StyleSheet,
  SafeAreaView,
  ScrollView,
  TouchableOpacity,
  Switch,
  Alert,
} from 'react-native';
import Icon from 'react-native-vector-icons/MaterialIcons';
import LinearGradient from 'react-native-linear-gradient';
import * as Animatable from 'react-native-animatable';

const SettingsScreen = () => {
  const [settings, setSettings] = useState({
    highSafetyMode: true,
    accessibilityMode: false,
    personalization: true,
    notifications: true,
    locationServices: true,
    dataUsage: false,
    darkMode: false,
  });

  const handleToggle = (setting) => {
    setSettings(prev => ({
      ...prev,
      [setting]: !prev[setting],
    }));
  };

  const handleLogout = () => {
    Alert.alert(
      'Logout',
      'Are you sure you want to logout?',
      [
        {text: 'Cancel', style: 'cancel'},
        {text: 'Logout', style: 'destructive', onPress: () => {
          // Handle logout logic here
          Alert.alert('Logged out', 'You have been logged out successfully');
        }},
      ]
    );
  };

  const renderSettingItem = (title, description, settingKey, icon, color = '#2E7D32') => (
    <Animatable.View animation="fadeInRight" style={styles.settingItem}>
      <View style={styles.settingLeft}>
        <View style={[styles.settingIcon, {backgroundColor: color}]}>
          <Icon name={icon} size={20} color="#FFFFFF" />
        </View>
        <View style={styles.settingInfo}>
          <Text style={styles.settingTitle}>{title}</Text>
          <Text style={styles.settingDescription}>{description}</Text>
        </View>
      </View>
      <Switch
        value={settings[settingKey]}
        onValueChange={() => handleToggle(settingKey)}
        trackColor={{false: '#E0E0E0', true: '#A5D6A7'}}
        thumbColor={settings[settingKey] ? '#2E7D32' : '#FFFFFF'}
      />
    </Animatable.View>
  );

  const renderSection = (title, children) => (
    <Animatable.View animation="fadeInUp" style={styles.section}>
      <Text style={styles.sectionTitle}>{title}</Text>
      <View style={styles.sectionContent}>
        {children}
      </View>
    </Animatable.View>
  );

  const renderActionItem = (title, description, icon, color, onPress) => (
    <TouchableOpacity style={styles.actionItem} onPress={onPress}>
      <View style={styles.settingLeft}>
        <View style={[styles.settingIcon, {backgroundColor: color}]}>
          <Icon name={icon} size={20} color="#FFFFFF" />
        </View>
        <View style={styles.settingInfo}>
          <Text style={styles.settingTitle}>{title}</Text>
          <Text style={styles.settingDescription}>{description}</Text>
        </View>
      </View>
      <Icon name="chevron-right" size={20} color="#666" />
    </TouchableOpacity>
  );

  return (
    <SafeAreaView style={styles.container}>
      <LinearGradient
        colors={['#E8F5E8', '#F0F8F0']}
        style={styles.gradient}>
        
        <ScrollView style={styles.content} showsVerticalScrollIndicator={false}>
          
          {/* Safety & Accessibility */}
          {renderSection('Safety & Accessibility', [
            renderSettingItem(
              'High Safety Mode',
              'Prioritize safest routes with well-lit areas',
              'highSafetyMode',
              'security',
              '#FF5722'
            ),
            renderSettingItem(
              'Accessibility Mode',
              'Enhanced support for users with disabilities',
              'accessibilityMode',
              'accessibility',
              '#2196F3'
            ),
          ])}

          {/* Personalization */}
          {renderSection('Personalization', [
            renderSettingItem(
              'Personalization',
              'Customize recommendations based on your preferences',
              'personalization',
              'person',
              '#9C27B0'
            ),
            renderSettingItem(
              'Dark Mode',
              'Switch to dark theme for better visibility',
              'darkMode',
              'dark-mode',
              '#424242'
            ),
          ])}

          {/* Notifications */}
          {renderSection('Notifications', [
            renderSettingItem(
              'Push Notifications',
              'Receive updates about your routes and travel',
              'notifications',
              'notifications',
              '#FF9800'
            ),
            renderSettingItem(
              'Location Services',
              'Allow access to location for better recommendations',
              'locationServices',
              'location-on',
              '#4CAF50'
            ),
          ])}

          {/* Data & Privacy */}
          {renderSection('Data & Privacy', [
            renderSettingItem(
              'Data Usage Optimization',
              'Reduce data usage for slower connections',
              'dataUsage',
              'data-usage',
              '#607D8B'
            ),
          ])}

          {/* Account Actions */}
          {renderSection('Account', [
            renderActionItem(
              'Edit Profile',
              'Update your personal information',
              'edit',
              '#2E7D32',
              () => Alert.alert('Edit Profile', 'Profile editing feature coming soon!')
            ),
            renderActionItem(
              'Privacy Settings',
              'Manage your privacy and data sharing',
              'privacy-tip',
              '#FF5722',
              () => Alert.alert('Privacy Settings', 'Privacy settings feature coming soon!')
            ),
            renderActionItem(
              'Help & Support',
              'Get help and contact support',
              'help',
              '#2196F3',
              () => Alert.alert('Help & Support', 'Help center feature coming soon!')
            ),
          ])}

          {/* App Info */}
          {renderSection('App Information', [
            renderActionItem(
              'About UrbanPulse+',
              'Version 1.0.0 - Learn more about the app',
              'info',
              '#9C27B0',
              () => Alert.alert('About UrbanPulse+', 'UrbanPulse+ v1.0.0\nSmart Urban Travel Assistant\nBuilt with React Native')
            ),
            renderActionItem(
              'Terms & Conditions',
              'Read our terms of service',
              'description',
              '#607D8B',
              () => Alert.alert('Terms & Conditions', 'Terms and conditions feature coming soon!')
            ),
          ])}

          {/* Logout Button */}
          <Animatable.View animation="fadeInUp" delay={200} style={styles.logoutSection}>
            <TouchableOpacity style={styles.logoutButton} onPress={handleLogout}>
              <Icon name="logout" size={20} color="#FFFFFF" />
              <Text style={styles.logoutButtonText}>Logout</Text>
            </TouchableOpacity>
          </Animatable.View>

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
  section: {
    marginTop: 20,
    marginBottom: 10,
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#2E7D32',
    marginBottom: 15,
    marginLeft: 5,
  },
  sectionContent: {
    backgroundColor: '#FFFFFF',
    borderRadius: 15,
    shadowColor: '#000',
    shadowOffset: {width: 0, height: 2},
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 4,
  },
  settingItem: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    padding: 20,
    borderBottomWidth: 1,
    borderBottomColor: '#F0F0F0',
  },
  actionItem: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    padding: 20,
    borderBottomWidth: 1,
    borderBottomColor: '#F0F0F0',
  },
  settingLeft: {
    flexDirection: 'row',
    alignItems: 'center',
    flex: 1,
  },
  settingIcon: {
    width: 40,
    height: 40,
    borderRadius: 20,
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: 15,
  },
  settingInfo: {
    flex: 1,
  },
  settingTitle: {
    fontSize: 16,
    fontWeight: '600',
    color: '#333',
    marginBottom: 4,
  },
  settingDescription: {
    fontSize: 14,
    color: '#666',
    lineHeight: 20,
  },
  logoutSection: {
    marginTop: 30,
    marginBottom: 30,
  },
  logoutButton: {
    backgroundColor: '#F44336',
    borderRadius: 15,
    padding: 20,
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    shadowColor: '#000',
    shadowOffset: {width: 0, height: 2},
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 4,
  },
  logoutButtonText: {
    color: '#FFFFFF',
    fontSize: 16,
    fontWeight: 'bold',
    marginLeft: 10,
  },
});

export default SettingsScreen;
