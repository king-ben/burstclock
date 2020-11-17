package beast.evolution.branchratemodel;

import beast.core.Description;
import beast.core.Input;
import beast.core.parameter.RealParameter;
import beast.evolution.tree.Node;

@Description("Clock model with a constant contribution from each split in the tree, on top of the specified ´metaClock´ branch rate model")
public class SemiStrictClock extends StrictClockModel {

    public Input<RealParameter> persplitInput = new Input<>("perSplit",
			"Effective number of changes after each split in the tree",
            Input.Validate.REQUIRED);

    public Input<BranchRateModel.Base> metaClockInput = new Input<>("metaClock",
            "The clock model defining the rate along different branches (ignoring splits).");

	public Input<RealParameter> birthrateInput = new Input<RealParameter>("birthrate",
			"Birth rate (not effective diversification rate) of the tree, used to infer additional changes after unobserved splits. (Not necessary, but likely makes for better mixing.)",
			new RealParameter(new Double[] { 0. }));

    BranchRateModel.Base metaClock;

    @Override
    public void initAndValidate() {
        metaClock = metaClockInput.get();
        if (metaClock == null) {
            // If no meta clock is specified, use a  is a strict clock. 
            metaClock = new StrictClockModel();
            metaClock.initByName("clock.rate", meanRateInput.get());
        }
    }

	@Override
	public double getRateForBranch(final Node node) {
        double perSplit = persplitInput.get().getValue();
        double birthRate = birthrateInput.get().getValue();
        double metaRate = metaClock.getRateForBranch(node);
        double blength = node.getLength();

        double splits = 1 + blength * birthRate;
        return Math.max(metaRate, (splits * perSplit + blength * metaRate) / blength);
	}
}
