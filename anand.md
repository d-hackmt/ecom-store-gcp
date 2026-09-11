Straight answer: no, not yet — here's exactly why, and my recommendation on the region question.

Is it ultra-low-latency and smooth right now?
Not confirmed, for three concrete reasons:

The Cloud Run cold-start fix (--min-instances) still isn't in the real cloudbuild.yaml — I flagged that last turn and you moved to the region question before confirming you wanted it added. So as of right now, both main-app and store still scale to zero and still cold-start.
The Mongo/Cloud-Run region mismatch is still live — every DB call still pays the Mumbai↔Iowa round trip. This is probably the single biggest remaining latency cost.
I genuinely don't know if a deploy has even happened since our code pushes. Cloud Build needs a trigger (GitHub App trigger, or you running gcloud builds submit manually) to actually pick up the new commits — pushing to GitHub doesn't deploy anything by itself unless that trigger exists and fired. I have no visibility into your Cloud Build history from here.
So: the app-code fixes (image bloat, request timeout, login gate, cart caching) are real and will make things meaningfully snappier once deployed, but I can't honestly tell you the live app is smooth right now without either (a) you confirming a deploy ran, or (b) giving me the live URL so I can actually hit it and check response times/payload sizes myself rather than guessing.

MongoDB region — my recommendation: move Cloud Run to asia-south1, not Mongo to us-central1
Two ways to fix the mismatch, and they're not equivalent:

Move Cloud Run → asia-south1 (Mumbai): Cloud Run is stateless — this is just changing --region in cloudbuild.yaml and redeploying. Low risk, no data migration, no downtime.
Move MongoDB → us-central1 (Iowa): Atlas cluster migration is a stateful operation — provisioning a new region, migrating live data, cutting over the connection string, real risk of downtime or sync issues during cutover.
Beyond risk, there's a second factor: your storefront prices everything in ₹ (rupees) throughout the codebase, which strongly suggests your actual customers are in India. If that's right, moving Cloud Run to Mumbai fixes two problems at once — server↔database latency and customer↔server latency (Cloud Run gets close to your users too). Moving MongoDB to Iowa only fixes the first one; your actual customers would still be hitting a US-based server from India regardless.

So: move Cloud Run to asia-south1, unless your actual customer base is US-based (in which case the calculus flips and Mongo should move to us-central1 instead). Can you confirm where your customers actually are? That's the one thing I need to be sure before recommending you act on this.