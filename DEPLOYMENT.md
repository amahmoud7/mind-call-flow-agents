# Railway Deployment Guide

This guide will help you deploy the Mind Call Flow agents to Railway, enabling 24/7 availability for your Vercel frontend.

## Prerequisites

1. A Railway account (sign up at https://railway.app)
2. Your GitHub repository pushed with the latest code
3. All API credentials ready (LiveKit, OpenAI, Deepgram, Cartesia)

## Step 1: Create New Railway Project

1. Go to https://railway.app/dashboard
2. Click **"New Project"**
3. Select **"Deploy from GitHub repo"**
4. Authorize Railway to access your GitHub account
5. Select the **mind-call-flow** repository
6. Railway will automatically detect the agent directory

## Step 2: Configure Build Settings

1. In your Railway project, go to **Settings**
2. Under **Build**, set:
   - **Root Directory**: `agent`
   - **Builder**: Dockerfile (should auto-detect)
3. Save changes

## Step 3: Add Environment Variables

Go to the **Variables** tab and add the following:

### Required Variables:

```
LIVEKIT_URL=wss://akrams-voice-agents-yqfg2we8.livekit.cloud
LIVEKIT_API_KEY=APIZoEnLySuUYBb
LIVEKIT_API_SECRET=KIbd2ecvlUW8ljYNFEq0XXPeFlbTjmbWP09mYNyGR3a
OPENAI_API_KEY=sk-proj-8PAzUlthPK1M-ztY0wYvopJWQkUS...
DEEPGRAM_API_KEY=71796793681390ae078cf6699cde159a1b900704
CARTESIA_API_KEY=sk_car_n5Mtpdnehcm7a9nt7CTtBk
ELEVENLABS_API_KEY=sk_b2a3bcc591746d781aae3d1981660e24a2c067fa5d3574a3
```

### Optional (for Twilio outbound calling):

```
TWILIO_ACCOUNT_SID=your_twilio_account_sid
TWILIO_AUTH_TOKEN=your_twilio_auth_token
TWILIO_PHONE_NUMBER=+1234567890
```

## Step 4: Deploy

1. Click **"Deploy"** button
2. Railway will:
   - Build the Docker image
   - Install all Python dependencies
   - Start the multi-agent runner
3. Monitor the deployment logs to ensure all 4 agents start successfully

## Step 5: Verify Deployment

In the deployment logs, you should see:

```
Starting all LiveKit agents...
Started process: general-assistant
Started process: scheduling-agent
Started process: customer-service-agent
Started process: outbound-caller-agent
```

## Step 6: Test the Connection

1. Go to your Vercel site: https://mind-call-flow.vercel.app
2. Click "Start Conversation" with the General Assistant
3. You should now be able to have voice conversations!

## Monitoring

- Railway provides logs in real-time
- Check the **Metrics** tab for CPU/Memory usage
- The service will auto-restart if it crashes

## Cost Estimate

- **Railway Free Tier**: $5 of free credits per month
- **Estimated Cost**: ~$5-10/month for continuous operation
- **Alternative**: Use Railway's hobby plan for $5/month with more resources

## Troubleshooting

### Issue: Agents not connecting
- Check that all environment variables are set correctly
- Verify LiveKit credentials in Railway dashboard
- Check deployment logs for errors

### Issue: High memory usage
- LiveKit agents use ~200-300MB per agent
- Total expected: ~1GB RAM for all 4 agents
- Consider upgrading Railway plan if needed

### Issue: Service keeps restarting
- Check logs for Python errors
- Ensure all dependencies are in requirements.txt
- Verify API keys are valid

## Alternative: Deploy to Other Platforms

If you prefer a different platform, you can also deploy to:

- **Render**: Similar to Railway, free tier available
- **Fly.io**: Good for long-running processes
- **AWS ECS/Fargate**: More complex but highly scalable
- **Google Cloud Run**: Serverless option (may have cold starts)

The Dockerfile and environment variables remain the same across all platforms.
