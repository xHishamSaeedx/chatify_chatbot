"""
Microservice Adapter
Optimizes the chatbot service for backend-to-backend communication
"""

import asyncio
import logging
from datetime import datetime
from typing import Dict, Any, Optional, List
from app.services.session_service import session_service
from app.services.openai_service import openai_service
from app.services.firebase_service import firebase_service
from app.services.analytics_service import analytics_service

# Configure logging
logger = logging.getLogger(__name__)

class MicroserviceAdapter:
    """
    Adapter layer for optimizing chatbot service as a microservice
    Provides clean interfaces for backend orchestrator communication
    """
    
    def __init__(self):
        self.service_name = "Chatify Chatbot Microservice"
        self.version = "2.0.0"
        self.startup_time = datetime.utcnow()
        
        # Service metrics
        self.metrics = {
            'total_sessions_created': 0,
            'total_messages_processed': 0,
            'active_sessions': 0,
            'avg_response_time_ms': 0,
            'last_cleanup_time': None,
            'errors_count': 0
        }
        
        logger.info(f"🤖 [MICROSERVICE] {self.service_name} v{self.version} initialized")
    
    async def create_session_optimized(
        self, 
        user_id: str, 
        template_id: str = "general-assistant",
        orchestrator_metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Create AI session optimized for microservice communication
        
        Args:
            user_id: User identifier from orchestrator
            template_id: Personality template ID
            orchestrator_metadata: Metadata from backend orchestrator
            
        Returns:
            Session creation result with microservice metadata
        """
        start_time = datetime.utcnow()
        
        try:
            logger.info(f"🚀 [MICROSERVICE] Creating session for user {user_id}, template: {template_id}")
            
            # Create session through existing session service
            result = await session_service.create_session(user_id, template_id)
            
            if result.get("success"):
                self.metrics['total_sessions_created'] += 1
                self.metrics['active_sessions'] = len(session_service.active_sessions)
                
                # Add microservice metadata
                result['microservice'] = {
                    'service_name': self.service_name,
                    'version': self.version,
                    'processing_time_ms': (datetime.utcnow() - start_time).total_seconds() * 1000,
                    'orchestrator_metadata': orchestrator_metadata,
                    'created_at': datetime.utcnow().isoformat()
                }
                
                logger.info(f"✅ [MICROSERVICE] Session created: {result['session_id']} (took {result['microservice']['processing_time_ms']:.1f}ms)")
                
            return result
            
        except Exception as e:
            self.metrics['errors_count'] += 1
            logger.error(f"❌ [MICROSERVICE] Session creation failed for user {user_id}: {e}")
            
            return {
                "success": False,
                "error": str(e),
                "microservice": {
                    'service_name': self.service_name,
                    'version': self.version,
                    'error_type': 'session_creation_failed',
                    'processing_time_ms': (datetime.utcnow() - start_time).total_seconds() * 1000
                }
            }
    
    async def send_message_optimized(
        self, 
        session_id: str, 
        user_message: str,
        orchestrator_metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Send message to AI optimized for microservice communication
        
        Args:
            session_id: Session identifier
            user_message: User's message content
            orchestrator_metadata: Metadata from backend orchestrator
            
        Returns:
            Message processing result with microservice metadata
        """
        start_time = datetime.utcnow()
        
        try:
            logger.info(f"💬 [MICROSERVICE] Processing message for session {session_id} (length: {len(user_message)})")
            
            # Send message through existing session service
            result = await session_service.send_message(session_id, user_message)
            
            if result.get("success"):
                self.metrics['total_messages_processed'] += 1
                
                # Calculate and update average response time
                processing_time_ms = (datetime.utcnow() - start_time).total_seconds() * 1000
                if self.metrics['avg_response_time_ms'] == 0:
                    self.metrics['avg_response_time_ms'] = processing_time_ms
                else:
                    # Moving average
                    self.metrics['avg_response_time_ms'] = (
                        self.metrics['avg_response_time_ms'] * 0.9 + processing_time_ms * 0.1
                    )
                
                # Add microservice metadata
                result['microservice'] = {
                    'service_name': self.service_name,
                    'version': self.version,
                    'processing_time_ms': processing_time_ms,
                    'avg_response_time_ms': self.metrics['avg_response_time_ms'],
                    'orchestrator_metadata': orchestrator_metadata,
                    'processed_at': datetime.utcnow().isoformat()
                }
                
                logger.info(f"✅ [MICROSERVICE] Message processed for session {session_id} (took {processing_time_ms:.1f}ms)")
                
            return result
            
        except Exception as e:
            self.metrics['errors_count'] += 1
            logger.error(f"❌ [MICROSERVICE] Message processing failed for session {session_id}: {e}")
            
            return {
                "success": False,
                "error": str(e),
                "microservice": {
                    'service_name': self.service_name,
                    'version': self.version,
                    'error_type': 'message_processing_failed',
                    'processing_time_ms': (datetime.utcnow() - start_time).total_seconds() * 1000
                }
            }
    
    async def end_session_optimized(
        self, 
        session_id: str,
        orchestrator_metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        End AI session optimized for microservice communication
        
        Args:
            session_id: Session identifier
            orchestrator_metadata: Metadata from backend orchestrator
            
        Returns:
            Session termination result with microservice metadata
        """
        start_time = datetime.utcnow()
        
        try:
            logger.info(f"🔚 [MICROSERVICE] Ending session {session_id}")
            
            # End session through existing session service
            result = await session_service.end_session(session_id)
            
            if result.get("success"):
                self.metrics['active_sessions'] = len(session_service.active_sessions)
                
                # Add microservice metadata
                result['microservice'] = {
                    'service_name': self.service_name,
                    'version': self.version,
                    'processing_time_ms': (datetime.utcnow() - start_time).total_seconds() * 1000,
                    'orchestrator_metadata': orchestrator_metadata,
                    'ended_at': datetime.utcnow().isoformat()
                }
                
                logger.info(f"✅ [MICROSERVICE] Session ended: {session_id}")
                
            return result
            
        except Exception as e:
            self.metrics['errors_count'] += 1
            logger.error(f"❌ [MICROSERVICE] Session termination failed for {session_id}: {e}")
            
            return {
                "success": False,
                "error": str(e),
                "microservice": {
                    'service_name': self.service_name,
                    'version': self.version,
                    'error_type': 'session_termination_failed',
                    'processing_time_ms': (datetime.utcnow() - start_time).total_seconds() * 1000
                }
            }
    
    def get_service_health(self) -> Dict[str, Any]:
        """
        Get comprehensive service health information
        
        Returns:
            Service health status and metrics
        """
        uptime_seconds = (datetime.utcnow() - self.startup_time).total_seconds()
        
        # Check service dependencies
        dependencies = {
            'session_service': True,  # Always available (in-memory)
            'openai_service': True,   # Check if API key is set
            'firebase_service': True,  # Check Firebase connection
        }
        
        # Check OpenAI service
        try:
            dependencies['openai_service'] = openai_service.client is not None
        except:
            dependencies['openai_service'] = False
        
        # Check Firebase service
        try:
            dependencies['firebase_service'] = firebase_service.is_initialized()
        except:
            dependencies['firebase_service'] = False
        
        # Overall health status
        is_healthy = all(dependencies.values()) and self.metrics['errors_count'] < 100
        
        return {
            'status': 'healthy' if is_healthy else 'degraded',
            'service': self.service_name,
            'version': self.version,
            'uptime_seconds': uptime_seconds,
            'uptime_formatted': f"{uptime_seconds // 3600:.0f}h {(uptime_seconds % 3600) // 60:.0f}m",
            'dependencies': dependencies,
            'metrics': self.metrics.copy(),
            'active_sessions': len(session_service.active_sessions),
            'timestamp': datetime.utcnow().isoformat()
        }
    
    def get_service_stats(self) -> Dict[str, Any]:
        """
        Get detailed service statistics
        
        Returns:
            Comprehensive service statistics
        """
        # Get session service stats
        session_stats = {
            'active_sessions': len(session_service.active_sessions),
            'sessions_by_personality': {},
        }
        
        # Count sessions by personality
        for session_data in session_service.active_sessions.values():
            template_id = session_data.get('template_id', 'unknown')
            session_stats['sessions_by_personality'][template_id] = (
                session_stats['sessions_by_personality'].get(template_id, 0) + 1
            )
        
        return {
            'service': self.service_name,
            'version': self.version,
            'uptime_seconds': (datetime.utcnow() - self.startup_time).total_seconds(),
            'metrics': self.metrics.copy(),
            'session_stats': session_stats,
            'last_cleanup': self.metrics.get('last_cleanup_time'),
            'timestamp': datetime.utcnow().isoformat()
        }
    
    async def cleanup_service(self) -> Dict[str, Any]:
        """
        Perform service cleanup operations
        
        Returns:
            Cleanup operation results
        """
        start_time = datetime.utcnow()
        
        try:
            logger.info("🧹 [MICROSERVICE] Starting cleanup operations...")
            
            # Run session cleanup
            await session_service.cleanup_expired_sessions()
            
            # Update cleanup metrics
            self.metrics['last_cleanup_time'] = datetime.utcnow().isoformat()
            self.metrics['active_sessions'] = len(session_service.active_sessions)
            
            cleanup_time_ms = (datetime.utcnow() - start_time).total_seconds() * 1000
            
            logger.info(f"✅ [MICROSERVICE] Cleanup completed in {cleanup_time_ms:.1f}ms")
            
            return {
                'success': True,
                'cleanup_time_ms': cleanup_time_ms,
                'active_sessions_after': self.metrics['active_sessions'],
                'timestamp': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ [MICROSERVICE] Cleanup failed: {e}")
            return {
                'success': False,
                'error': str(e),
                'cleanup_time_ms': (datetime.utcnow() - start_time).total_seconds() * 1000
            }

# Global microservice adapter instance
microservice_adapter = MicroserviceAdapter()

